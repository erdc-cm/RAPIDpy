# -*- coding: utf-8 -*-
##
##  muskingum.py
##  RAPIDpy
##
##  Created by Alan D Snow.
##
##  Copyright © 2016 Alan D Snow. All rights reserved.
##  License: BSD 3-Clause

from csv import reader as csv_reader
from csv import writer as csv_writer
import numpy as np
from past.builtins import xrange

try:
    from osgeo import gdal, ogr
except Exception:
    raise Exception("You need the gdal python package to run this tool ...")

# Enable GDAL/OGR exceptions
gdal.UseExceptions()
   
#local
from ..helper_functions import csv_to_list, open_csv

def CreateMuskingumKfacFile(in_drainage_line,
                            river_id,
                            length_id,
                            slope_id,
                            celerity,
                            formula_type,
                            in_connectivity_file,
                            out_kfac_file,
                            length_units="km",
                            file_geodatabase=None):
    """
    Creates the Kfac file for calibration.

    Formula Type Options:
    
    1. River Length/Celerity; 
    2. Eta*River Length/Sqrt(River Slope); and 3 is
    3. Eta*River Length/Sqrt(River Slope) [0.05, 0.95]
    
    Where Eta = Average(River Length/Co of all rivers) / Average(River Length/Sqrt(River Slope) of all rivers)
    
    Args:
        in_drainage_line(str): Path to the stream network (i.e. Drainage Line) shapefile.
        river_id(str): The name of the field with the river ID (Ex. 'HydroID', 'COMID', or 'LINKNO').
        length_id(str): The field name containging the length of the river segment (Ex. 'LENGTHKM' or 'Length').
        slope_id(str): The field name containging the slope of the river segment (Ex. 'Avg_Slope' or 'Slope').
        celerity(float): The flow wave celerity for the watershed in meters per second. 1 km/hr or 1000.0/3600.0 m/s is a reasonable value if unknown.
        formula_type(int): An integer representing the formula type to use when calculating kfac. 
        in_connectivity_file(str): The path to the RAPID connectivity file.
        out_kfac_file(str): The path to the output kfac file.
        length_units(str): The units for the length_id field. Supported types are "m" for meters and "km" for kilometers.
        file_geodatabase(Optional[str]): Path to the file geodatabase. If you use this option, in_drainage_line is the name of the stream network feature class. (WARNING: Not always stable with GDAL.)
    
    Example::
    
        from RAPIDpy.gis.muskingum import CreateMuskingumKfacFile
        #------------------------------------------------------------------------------
        #main process
        #------------------------------------------------------------------------------
        if __name__ == "__main__":
            CreateMuskingumKfacFile(in_drainage_line='/path/to/drainageline.shp',
                                    river_id='LINKNO',
                                    length_id='Length',
                                    slope_id='Slope',
                                    celerity=1000.0/3600.0,
                                    formula_type=3,
                                    in_connectivity_file='/path/to/rapid_connect.csv',
                                    out_kfac_file='/path/to/kfac.csv',
                                    length_units="m",
                                    )    
    """
    if file_geodatabase:
        gdb_driver = ogr.GetDriverByName("OpenFileGDB")
        ogr_file_geodatabase = gdb_driver.Open(file_geodatabase)
        ogr_drainage_line_shapefile_lyr = ogr_file_geodatabase.GetLayer(in_drainage_line)
    else:
        ogr_drainage_line_shapefile = ogr.Open(in_drainage_line)
        ogr_drainage_line_shapefile_lyr = ogr_drainage_line_shapefile.GetLayer()

    number_of_features = ogr_drainage_line_shapefile_lyr.GetFeatureCount()
    river_id_list = np.zeros(number_of_features, dtype=np.int32)
    length_list = np.zeros(number_of_features, dtype=np.float32)
    slope_list = np.zeros(number_of_features, dtype=np.float32)
    for feature_idx, drainage_line_feature in enumerate(ogr_drainage_line_shapefile_lyr):
        river_id_list[feature_idx] = drainage_line_feature.GetField(river_id)
        length = drainage_line_feature.GetField(length_id)
        if length is not None:
            length_list[feature_idx] = length
        slope = drainage_line_feature.GetField(slope_id)
        if slope is not None:
            slope_list[feature_idx] = slope

    if length_units == "m":
        length_list = length_list/1000.0
    elif length_units != "km":
        raise Exception("ERROR: Invalid length units supplied. Supported units are m and km.")
        
    connectivity_table = np.loadtxt(in_connectivity_file, 
                                    delimiter=",", 
                                    dtype=int)
    
    length_slope_array = []
    kfac2_array = []
    if formula_type == 1:
        print("River Length/Celerity")
    elif formula_type == 2:
        print("Eta*River Length/Sqrt(River Slope)")
    elif formula_type == 3:
        print("Eta*River Length/Sqrt(River Slope) [0.05, 0.95]")
    else:
        raise Exception("Invalid formula type. Valid range: 1-3 ...")
    
    with open_csv(out_kfac_file,'w') as kfacfile:
        kfac_writer = csv_writer(kfacfile)
        for row in connectivity_table:
            streamID = int(float(row[0]))
            
            streamIDindex = river_id_list==streamID
            # find the length
            stream_length = length_list[streamIDindex]*1000

            if formula_type >= 2:
                # find the slope
                stream_slope = slope_list[streamIDindex]
                
                if stream_slope <= 0:
                    #if no slope, take average of upstream and downstream to get it
                    nextDownID = int(float(row[1]))
                    next_down_slope = 0
                    try:
                        next_down_index = np.where(river_id_list==nextDownID)[0][0]
                        next_down_slope = slope_list[next_down_index]
                    except IndexError:
                        pass
                        
                    nextUpID = int(float(row[3]))
                    next_up_slope = 0
                    try:
                        next_up_index = np.where(river_id_list==nextUpID)[0][0]
                        next_up_slope = slope_list[next_up_index]
                    except IndexError:
                        pass
                        
                    stream_slope = (next_down_slope+next_up_slope)/2
                    if stream_slope <=0:
                        #if still no slope, set to 0.001
                        stream_slope = 0.001
                
                length_slope_array.append(stream_length/stream_slope**0.5)
                kfac2_array.append(stream_length/celerity)
            else:
                kfac = stream_length/celerity
                kfac_writer.writerow(kfac)
        
        if formula_type >= 2:
            if formula_type == 3:
                print("Filtering Data by 5th and 95th Percentiles ...")
                length_slope_array = np.array(length_slope_array)
                percentile_5 = np.percentile(length_slope_array, 5)
                percentile_95 = np.percentile(length_slope_array, 95)
                
                length_slope_array[length_slope_array<percentile_5] = percentile_5
                length_slope_array[length_slope_array>percentile_95] = percentile_95
            
            eta = np.mean(kfac2_array) / np.mean(length_slope_array)
            print("Kfac2_Avg {0}".format(np.mean(kfac2_array)))
            print("Length_Slope Avg {0}".format( np.mean(length_slope_array)))
            print("Eta {0}".format(eta))
            print("Writing Data ...")
            for len_slope in length_slope_array:
                kfac_writer.writerow(eta*len_slope)

def CreateMuskingumKFile(lambda_k,
                         in_kfac_file,
                         out_k_file):
    """
    Creates muskingum k file from kfac file.
    
    Args:
        lambda_k(float): The value for lambda given from RAPID after the calibration process. If no calibration has been performed, 0.35 is reasonable.
        in_kfac_file(str): The path to the input kfac file.
        out_k_file(str): The path to the output k file.
    
    Example::
    
        from RAPIDpy.gis.muskingum import CreateMuskingumKFile
        #------------------------------------------------------------------------------
        #main process
        #------------------------------------------------------------------------------
        if __name__ == "__main__":
            CreateMuskingumKFile(lambda_k=0.35,
                                 in_kfac_file='/path/to/kfac.csv',
                                 out_k_file='/path/to/k.csv',
                                 )
    """
    kfac_table = csv_to_list(in_kfac_file)
    
    with open_csv(out_k_file,'w') as kfile:
        k_writer = csv_writer(kfile)
        for row in kfac_table:
             k_writer.writerow([lambda_k*float(row[0])])

def CreateMuskingumXFileFromDranageLine(in_drainage_line,
                                        x_id,
                                        out_x_file,
                                        file_geodatabase=None):
    """
    Create muskingum X file from drainage line.

    Args:
        in_drainage_line(str): Path to the stream network (i.e. Drainage Line) shapefile.
        x_id(str): The name of the muksingum X field (i.e. 'Musk_x').
        out_x_file(str): The path to the output x file.
        file_geodatabase(Optional[str]): Path to the file geodatabase. If you use this option, in_drainage_line is the name of the stream network feature class. (WARNING: Not always stable with GDAL.)
    
    Example::
    
        from RAPIDpy.gis.muskingum import CreateMuskingumXFileFromDranageLine
        #------------------------------------------------------------------------------
        #main process
        #------------------------------------------------------------------------------
        if __name__ == "__main__":
            CreateMuskingumXFileFromDranageLine(in_drainage_line='/path/to/drainageline.shp',
                                                x_id='Musk_x',
                                                out_x_file='/path/to/x.csv',
                                                )
    """
    if file_geodatabase:
        gdb_driver = ogr.GetDriverByName("OpenFileGDB")
        ogr_file_geodatabase = gdb_driver.Open(file_geodatabase)
        ogr_drainage_line_shapefile_lyr = ogr_file_geodatabase.GetLayer(in_drainage_line)
    else:
        ogr_drainage_line_shapefile = ogr.Open(in_drainage_line)
        ogr_drainage_line_shapefile_lyr = ogr_drainage_line_shapefile.GetLayer()

    with open_csv(out_x_file,'w') as kfile:
        x_writer = csv_writer(kfile)
        for drainage_line_feature in ogr_drainage_line_shapefile_lyr:
            x_writer.writerow([drainage_line_feature.GetField(x_id)])    

def CreateConstMuskingumXFile(x_value,
                              in_connectivity_file,
                              out_x_file):
    """
    Create muskingum X file from value that is constant all the way through for each river segment.
    
    Args:
        x_value(float): Value for the muskingum X parameter [0-0.5].
        in_connectivity_file(str): The path to the RAPID connectivity file.
        out_x_file(str): The path to the output x file.
    
    Example::
    
        from RAPIDpy.gis.muskingum import CreateConstMuskingumXFile
        #------------------------------------------------------------------------------
        #main process
        #------------------------------------------------------------------------------
        if __name__ == "__main__":
            CreateConstMuskingumXFile(x_value=0.3,
                                      in_connectivity_file='/path/to/rapid_connect.csv',
                                      out_x_file='/path/to/x.csv',
                                      )
    """
    num_rivers = 0
    with open_csv(in_connectivity_file, "r") as csvfile:
        reader = csv_reader(csvfile)
        for row in reader:
            num_rivers+=1

    with open_csv(out_x_file,'w') as kfile:
        x_writer = csv_writer(kfile)
        for idx in xrange(num_rivers):
            x_writer.writerow([x_value])    