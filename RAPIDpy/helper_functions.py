# -*- coding: utf-8 -*-
##
##  helper_functions.py
##  RAPIDpy
##
##  Created by Alan D Snow, 2015.
##  Copyright © 2015 Alan D Snow. All rights reserved.
##
import csv
from numpy.testing import assert_almost_equal
from numpy import array as np_array
from numpy import float32 as np_float32
from os import remove
from sys import version_info

#------------------------------------------------------------------------------
# HELPER FUNCTIONS
#------------------------------------------------------------------------------
def open_csv(csv_file, mode='r'):
    """
    Get mode depending on Python version
    Based on: http://stackoverflow.com/questions/29840849/writing-a-csv-file-in-python-that-works-for-both-python-2-7-and-python-3-3-in
    """
    if version_info[0] == 2:  # Not named on 2.6
        access = '{0}b'.format(mode)
        kwargs = {}
    else:
        access = '{0}t'.format(mode)
        kwargs = {'newline':''}
        
    return open(csv_file, access, **kwargs)
        
def log(message, severity, print_debug=True):
    """Logs, prints, or raises a message.

    Arguments:
        message -- message to report
        severity -- string of one of these values:
            CRITICAL|ERROR|WARNING|INFO|DEBUG
    """

    print_me = ['WARNING', 'INFO', 'DEBUG']
    if severity in print_me:
        if severity == 'DEBUG':
            if print_debug:
                print("{0}: {1}".format(severity, message))
        else:
                print("{0}: {1}".format(severity, message))
    else:
        raise Exception("{0}: {1}".format(severity, message))

def csv_to_list(csv_file, delimiter=','):
    """
    Reads in a CSV file and returns the contents as list,
    where every row is stored as a sublist, and each element
    in the sublist represents 1 cell in the table.
    """
    with open_csv(csv_file) as csv_con:
        if len(delimiter) > 1:
            dialect = csv.Sniffer().sniff(csv_con.read(1024), delimiters=delimiter)
            csv_con.seek(0)
            reader = csv.reader(csv_con, dialect)
        else:
            reader = csv.reader(csv_con, delimiter=delimiter)
        return list(reader)

def compare_csv_decimal_files(file1, file2, header=True):
    """
    This function compares two csv files
    """
    #CHECK NUM LINES
    with open_csv(file1) as fh1, \
         open_csv(file2) as fh2:
         assert sum(1 for line1 in fh1) == sum(1 for line2 in fh2)
    
    with open_csv(file1) as fh1, \
         open_csv(file2) as fh2:
        csv1 = csv.reader(fh1)
        csv2 = csv.reader(fh2)
        files_equal = True
        if header:
            files_equal = (next(csv1) == next(csv2)) #header
        while files_equal:
            try:
                try:
                    assert_almost_equal(np_array(next(csv1), dtype=np_float32),
                                        np_array(next(csv2), dtype=np_float32),
                                        decimal=2)
                except AssertionError:
                    files_equal = False
                    break
                    pass
            except StopIteration:
                break
                pass
    return files_equal
    
def compare_csv_timeseries_files(file1, file2, header=True):
    """
    This function compares two csv files
    """
    #CHECK NUM LINES
    with open_csv(file1) as fh1, \
         open_csv(file2) as fh2:
         assert sum(1 for line1 in fh1) == sum(1 for line2 in fh2)

    with open_csv(file1) as fh1, \
         open_csv(file2) as fh2:
        csv1 = csv.reader(fh1)
        csv2 = csv.reader(fh2)
        files_equal = True
        if header:
            files_equal = (next(csv1) == next(csv2)) #header
        while files_equal:
            try:
                try:
                    row1 = next(csv1)
                    row2 = next(csv2)
                    files_equal = row1[0] == row2[0] #check dates
                    assert_almost_equal(np_array(row1[1:], dtype=np_float32),
                                        np_array(row2[1:], dtype=np_float32),
                                        decimal=2)
                except AssertionError:
                    files_equal = False
                    break
                    pass
            except StopIteration:
                break
                pass
    return files_equal

def remove_files(*args):
    """
    This function removes all files input as arguments
    """
    for arg in args:
        try:
            remove(arg)
        except OSError:
            pass

