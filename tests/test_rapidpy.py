# -*- coding: utf-8 -*-
##
##  test_rapidpy.py
##  RAPIDpy
##
##  Created by Alan D. Snow 2016.
##  Copyright © 2015 Alan D Snow. All rights reserved.
##

from datetime import datetime
from filecmp import cmp as fcmp
from netCDF4 import Dataset
from nose.tools import ok_
import os
from shutil import copy


#local import
from RAPIDpy.rapid import RAPID
from RAPIDpy.helper_functions import (compare_qout_files, 
                                      remove_files,
                                      write_flows_to_csv)


#GLOBAL VARIABLES
MAIN_TESTS_FOLDER = os.path.dirname(os.path.abspath(__file__))
COMPARE_DATA_PATH = os.path.join(MAIN_TESTS_FOLDER, 'compare_data')
INPUT_DATA_PATH = os.path.join(MAIN_TESTS_FOLDER, 'input_data')
OUTPUT_DATA_PATH = os.path.join(MAIN_TESTS_FOLDER, 'tmp_output_files')

#------------------------------------------------------------------------------
# MAIN TEST SCRIPTS
#------------------------------------------------------------------------------
def test_generate_rapid_input_file():
    """
    Checks RAPID input file generation with valid input
    """
    print "TEST 1: GENERATE NAMELIST FILE"
    rapid_manager = RAPID(rapid_executable_location="",
                          use_all_processors=True,                          
                          ZS_TauR = 24*3600, #duration of routing procedure (time step of runoff data)
                          ZS_dtR = 15*60, #internal routing time step
                          ZS_TauM = 12*24*3600, #total simulation time 
                          ZS_dtM = 24*3600 #input time step 
                         )
    rapid_manager.update_parameters(rapid_connect_file='rapid_connect.csv',
                                    Vlat_file='m3_riv.nc',
                                    riv_bas_id_file='riv_bas_id.csv',
                                    k_file='k.csv',
                                    x_file='x.csv',
                                    Qout_file='Qout.nc'
                                    )
    generated_input_file = os.path.join(OUTPUT_DATA_PATH, 
                                        "rapid_namelist-GENERATE")
    rapid_manager.generate_namelist_file(generated_input_file)
    generated_input_file_solution = os.path.join(COMPARE_DATA_PATH, 
                                                 "rapid_namelist-GENERATE-SOLUTION")


    ok_(fcmp(generated_input_file, generated_input_file_solution))
    
    remove_files(generated_input_file)

def test_update_rapid_input_file():
    """
    Checks RAPID input file update with valid input
    """
    print "TEST 2: UPDATE NAMELIST FILE"
    rapid_manager = RAPID(rapid_executable_location="",
                          use_all_processors=True,                          
                         )
    rapid_manager.update_parameters(rapid_connect_file='rapid_connect.csv',
                                    Vlat_file='m3_riv.nc',
                                    riv_bas_id_file='riv_bas_id.csv',
                                    k_file='k.csv',
                                    x_file='x.csv',
                                    Qout_file='Qout.nc'
                                    )

    original_input_file = os.path.join(INPUT_DATA_PATH, 
                                      "rapid_namelist_valid")
    
    updated_input_file = os.path.join(OUTPUT_DATA_PATH, 
                                      "rapid_namelist-UPDATE")

    copy(original_input_file, updated_input_file)
    rapid_manager.update_namelist_file(updated_input_file)
    updated_input_file_solution = os.path.join(COMPARE_DATA_PATH, 
                                               "rapid_namelist-UPDATE-SOLUTION")


    ok_(fcmp(updated_input_file, updated_input_file_solution))
    
    remove_files(updated_input_file)

def test_update_rapid_invalid_input_file():
    """
    Checks RAPID input file update with valid input
    """
    print "TEST 3: UPDATE WITH INVALID NAMELIST FILE"
    rapid_manager = RAPID(rapid_executable_location="",
                          use_all_processors=True,                          
                         )
    rapid_manager.update_parameters(rapid_connect_file='rapid_connect.csv',
                                    Vlat_file='m3_riv.nc',
                                    riv_bas_id_file='riv_bas_id.csv',
                                    k_file='k.csv',
                                    x_file='x.csv',
                                    Qout_file='Qout.nc'
                                    )

    original_input_file = os.path.join(INPUT_DATA_PATH, 
                                      "rapid_namelist_invalid")
    
    updated_input_file = os.path.join(OUTPUT_DATA_PATH, 
                                      "rapid_namelist-UPDATE-INVALID")

    copy(original_input_file, updated_input_file)
    rapid_manager.update_namelist_file(updated_input_file)
    updated_input_file_solution = os.path.join(COMPARE_DATA_PATH, 
                                               "rapid_namelist-UPDATE-INVALID-SOLUTION")


    ok_(fcmp(updated_input_file, updated_input_file_solution))
    
    remove_files(updated_input_file)

def test_update_rapid_numbers_input_file():
    """
    Checks RAPID input file update with number validation
    """
    print "TEST 4: GENERATE NUMBERS FOR NAMELIST FILE"
    rapid_manager = RAPID(rapid_executable_location="",
                          use_all_processors=True,
                          rapid_connect_file=os.path.join(INPUT_DATA_PATH, 'rapid_connect.csv'),
                          riv_bas_id_file=os.path.join(INPUT_DATA_PATH, 'riv_bas_id.csv'),
                         )
    rapid_manager.update_reach_number_data()
                          
    rapid_manager.update_parameters(rapid_connect_file='rapid_connect.csv',
                                    Vlat_file='m3_riv_bas_erai_t511_3hr_19800101to19800101.nc',
                                    riv_bas_id_file='riv_bas_id.csv',
                                    k_file='k.csv',
                                    x_file='x.csv',
                                    Qout_file='Qout.nc'
                                    )

    generated_input_file = os.path.join(OUTPUT_DATA_PATH, 
                                      "rapid_namelist-GENERATE-NUMBERS")

    rapid_manager.generate_namelist_file(generated_input_file)
                          
    generated_input_file_solution = os.path.join(COMPARE_DATA_PATH, 
                                               "rapid_namelist-GENERATE-NUMBERS-SOLUTION")


    ok_(fcmp(generated_input_file, generated_input_file_solution))
    
    remove_files(generated_input_file)

def test_qout_same():
    """
    Test function to compare RAPID simulation Qout
    """
    print "TEST 5: TEST COMPARE RAPID QOUT"
    input_qout_file = os.path.join(COMPARE_DATA_PATH, 'Qout_erai_t511_3hr_19800101.nc')
    input_qout_file_cf = os.path.join(COMPARE_DATA_PATH, 'Qout_erai_t511_3hr_19800101_CF.nc')
   
    ok_(compare_qout_files(input_qout_file, input_qout_file_cf))

def test_run_rapid_simulation():
    """
    Test Running RAPID Simulation
    """
    
    print "TEST 6: TEST RUNNING RAPID SIMULATION"
    rapid_executable_location = os.path.join(MAIN_TESTS_FOLDER,
                                             "..", "..",
                                             "rapid", "src", "rapid")
                                             
    generated_qout_file = os.path.join(OUTPUT_DATA_PATH, 'Qout_erai_t511_3hr_19800101.nc')



    rapid_manager = RAPID(rapid_executable_location,
                          num_processors=1,
                          rapid_connect_file=os.path.join(INPUT_DATA_PATH, 'rapid_connect.csv'),
                          riv_bas_id_file=os.path.join(INPUT_DATA_PATH, 'riv_bas_id.csv'),
                          Vlat_file=os.path.join(INPUT_DATA_PATH, 'm3_riv_bas_erai_t511_3hr_19800101.nc'),
                          k_file=os.path.join(INPUT_DATA_PATH, 'k.csv'),
                          x_file=os.path.join(INPUT_DATA_PATH, 'x.csv'),
                          ZS_dtM=10800,
                          ZS_dtR=900,
                          ZS_TauM=86400,
                          ZS_TauR=10800,
                          Qout_file=generated_qout_file
                         )
    rapid_manager.update_reach_number_data()
    rapid_manager.run()

    generated_qout_file_solution = os.path.join(COMPARE_DATA_PATH,
                                                'Qout_erai_t511_3hr_19800101.nc')

    #check Qout    
    ok_(compare_qout_files(generated_qout_file, generated_qout_file_solution))

    #check other info in netcdf file
    d1 = Dataset(generated_qout_file)
    d2 = Dataset(generated_qout_file_solution)
    ok_(d1.dimensions.keys() == d2.dimensions.keys())
    ok_(d1.variables.keys() == d2.variables.keys())
    ok_((d1.variables['rivid'][:] == d2.variables['rivid'][:]).all())
    d1.close()
    d2.close()

    remove_files(generated_qout_file)
    
def test_convert_file_to_be_cf_compliant():
    """
    Test Convert RAPID Output to be CF Compliant
    """
    print "TEST 7: TEST CONVERT RAPID OUTPUT TO CF COMPLIANT (COMID_LAT_LON_Z)"

    input_qout_file = os.path.join(COMPARE_DATA_PATH, 'Qout_erai_t511_3hr_19800101.nc')
    temp_qout_file = os.path.join(OUTPUT_DATA_PATH, 'Qout_erai_t511_3hr_19800101_test_cf.nc')
    copy(input_qout_file, temp_qout_file)
    
    rapid_manager = RAPID(rapid_executable_location="",
                          Qout_file=temp_qout_file,
                          rapid_connect_file=os.path.join(INPUT_DATA_PATH, 'rapid_connect.csv'),
                          ZS_TauR=3*3600)

    rapid_manager.make_output_CF_compliant(simulation_start_datetime=datetime(1980, 1, 1),
                                           comid_lat_lon_z_file=os.path.join(INPUT_DATA_PATH, 'comid_lat_lon_z.csv'),
                                           project_name="ERA Interim (T511 Grid) 3 Hourly Runoff Based Historical flows by US Army ERDC")

    cf_qout_file_solution = os.path.join(COMPARE_DATA_PATH,
                                         'Qout_erai_t511_3hr_19800101_CF.nc')

    #check Qout    
    ok_(compare_qout_files(temp_qout_file, cf_qout_file_solution))

    #check other info in netcdf file
    d1 = Dataset(temp_qout_file)
    d2 = Dataset(cf_qout_file_solution)
    ok_(d1.dimensions.keys() == d2.dimensions.keys())
    ok_(d1.variables.keys() == d2.variables.keys())
    ok_((d1.variables['time'][:] == d1.variables['time'][:]).all())
    ok_((d1.variables['rivid'][:] == d1.variables['rivid'][:]).all())
    ok_((d1.variables['lat'][:] == d1.variables['lat'][:]).all())
    ok_((d1.variables['lon'][:] == d1.variables['lon'][:]).all())
    d1.close()
    d2.close()
    
    remove_files(temp_qout_file)

def test_generate_qinit_file():
    """
    This tests the qinit file function to create an input qinit file for RAPID
    """
    print "TEST 8: TEST GENERATE QINIT FILE"
    rapid_manager = RAPID(rapid_executable_location="",
                          rapid_connect_file=os.path.join(INPUT_DATA_PATH, 'rapid_connect.csv')
                         )

    #test with original rapid outpur
    input_qout_file = os.path.join(COMPARE_DATA_PATH, 'Qout_erai_t511_3hr_19800101.nc')
    original_qout_file = os.path.join(OUTPUT_DATA_PATH, 'Qout_erai_t511_3hr_19800101.nc')
    copy(input_qout_file, original_qout_file)

    qinit_original_rapid_qout = os.path.join(OUTPUT_DATA_PATH, 'qinit_original_rapid_qout.csv')
    rapid_manager.update_parameters(Qout_file=original_qout_file)
    rapid_manager.generate_qinit_from_past_qout(qinit_file=qinit_original_rapid_qout)
    
    qinit_original_rapid_qout_solution = os.path.join(COMPARE_DATA_PATH, 'qinit_original_rapid_qout-SOLUTION.csv')
    ok_(fcmp(qinit_original_rapid_qout, qinit_original_rapid_qout_solution))

    #test with CF rapid output and alternate time index
    cf_input_qout_file = os.path.join(COMPARE_DATA_PATH, 'Qout_erai_t511_3hr_19800101_CF.nc')
    cf_qout_file = os.path.join(OUTPUT_DATA_PATH, 'Qout_erai_t511_3hr_19800101_CF.nc')
    copy(cf_input_qout_file, cf_qout_file)

    qinit_cf_rapid_qout = os.path.join(OUTPUT_DATA_PATH, 'qinit_cf_rapid_qout.csv')
    rapid_manager.update_parameters(Qout_file=cf_qout_file)
    rapid_manager.generate_qinit_from_past_qout(qinit_file=qinit_cf_rapid_qout,
                                                time_index=5)
                                                
    qinit_cf_rapid_qout_solution = os.path.join(COMPARE_DATA_PATH, 'qinit_cf_rapid_qout-SOLUTION.csv')
    ok_(fcmp(qinit_cf_rapid_qout, qinit_cf_rapid_qout_solution))

    remove_files(original_qout_file, 
                 qinit_original_rapid_qout,
                 cf_qout_file,
                 qinit_cf_rapid_qout
                 )

def test_extract_timeseries():
    """
    This tests extracting a timeseries from RAPID Qout file
    """
    print "TEST 9: TEST EXTRACT TIMESERIES FROM QINIT FILE"
    
    #for writing entire time series to file
    input_qout_file = os.path.join(COMPARE_DATA_PATH, 'Qout_erai_t511_3hr_19800101.nc')
    original_qout_file = os.path.join(OUTPUT_DATA_PATH, 'Qout_erai_t511_3hr_19800101.nc')
    copy(input_qout_file, original_qout_file)
    original_timeseries_file = os.path.join(OUTPUT_DATA_PATH, 'original_timeseries.csv')
    
    time_valid = write_flows_to_csv(original_qout_file,
                                    original_timeseries_file,
                                    reach_id=5785903)
    if time_valid:
        original_timeseries_file_solution = os.path.join(COMPARE_DATA_PATH, 'original_timeseries-SOLUTION.csv')
    else:
        original_timeseries_file_solution = os.path.join(COMPARE_DATA_PATH, 'original_timeseries-notime-SOLUTION.csv')
        
    ok_(fcmp(original_timeseries_file, original_timeseries_file_solution))
    
    #if file is CF compliant, you can write out daily average
    cf_input_qout_file = os.path.join(COMPARE_DATA_PATH, 'Qout_erai_t511_3hr_19800101_CF.nc')
    cf_qout_file = os.path.join(OUTPUT_DATA_PATH, 'Qout_erai_t511_3hr_19800101_CF.nc')
    copy(cf_input_qout_file, cf_qout_file)
    cf_timeseries_daily_file = os.path.join(OUTPUT_DATA_PATH, 'cf_timeseries_daily.csv')

    write_flows_to_csv(cf_qout_file,
                       cf_timeseries_daily_file,
                       reach_index=20,
                       daily=True)

    cf_timeseries_daily_file_solution = os.path.join(COMPARE_DATA_PATH, 'cf_timeseries_daily-SOLUTION.csv')    
    ok_(fcmp(cf_timeseries_daily_file, cf_timeseries_daily_file_solution))
    
    #if file is CF compliant, check write out timeseries
    cf_timeseries_file = os.path.join(OUTPUT_DATA_PATH, 'cf_timeseries.csv')
    write_flows_to_csv(cf_qout_file,
                       cf_timeseries_file,
                       reach_index=20)

    cf_timeseries_file_solution = os.path.join(COMPARE_DATA_PATH, 'cf_timeseries-SOLUTION.csv')    
    ok_(fcmp(cf_timeseries_file, cf_timeseries_file_solution))

    remove_files(original_timeseries_file, 
                 original_qout_file,
                 cf_timeseries_file,
                 cf_qout_file,
                 cf_timeseries_daily_file
                 )

    
    

if __name__ == '__main__':
    import nose
    nose.main()