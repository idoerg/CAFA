#!/usr/bin/env python

import os
import sys
import sqlite3

'''
    This is a wrapper script for connecting to a sqlite3 database and retrieving values from it.
    The script takes as input a sqlite db file, name of an outfile where the results would be stored
    in tab-delimited format.
    
    The script interactively asks the user to input the required query as a string. The format of a 
    a sqlite query is almost the same as a MySQL query.

    Usage:
    python fetch_values_from_db.py <name of db file> <name of output file>

'''

def fetch_data(infile,outfile, query):

    conn = sqlite3.connect(infile)
    with conn:
        conn.text_factory = str
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

        for row in rows:
            for i in range(len(row)):
                outfile.write(str(row[i]).rstrip('\n') + '\t')
            outfile.write('\n')

if __name__ == '__main__':

    input_db = sys.argv[1]
    outfile = open(sys.argv[2], 'w')

    query = raw_input("Please enter your search query : ")
    fetch_data(input_db, outfile, query)
