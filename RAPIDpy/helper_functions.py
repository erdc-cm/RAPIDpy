##
##  helper_functions.py
##  RAPIDpy
##
##  Created by Alan D Snow, 2015.
##  Copyright © 2015 Alan D Snow. All rights reserved.
##
from csv import reader as csvreader
#------------------------------------------------------------------------------
# HELPER FUNCTIONS
#------------------------------------------------------------------------------
def csv_to_list(csv_file, delimiter=','):
    """
    Reads in a CSV file and returns the contents as list,
    where every row is stored as a sublist, and each element
    in the sublist represents 1 cell in the table.

    """
    with open(csv_file, 'rb') as csv_con:
        reader = csvreader(csv_con, delimiter=delimiter)
        return list(reader)
