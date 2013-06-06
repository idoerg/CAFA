#!/usr/bin/python

import os
import sys
import re
from collections import defaultdict
import dbm
import subprocess

'''
   User supplied predictions will normally contain swiss-
   prot ids as identifiers. In such a case, mapping to the uniprot id
   is performed to maintain consistency
'''

def mapper_pred(infile):

    db1 = defaultdict()
    mapper_swiss = defaultdict()
    mapper_uni = defaultdict()

    outfile_name = infile + '.id_mapped'
    
    universal_map_file = open('idmapping_selected.tab', 'r')

    outfile_handle = open(outfile_name, 'w')

    prediction_file = open(infile, 'r')
    for data in prediction_file:
        fields = data.strip().split()
        db1[fields[0]] = '1'

    prediction_file.close()

    for protein in universal_map_file:
        cols = protein.strip().split()
        if db1.has_key(cols[0]):
            mapper_uni[cols[0]] = cols[0]
        
        elif db1.has_key(cols[1]):
            mapper_swiss[cols[1]] = cols[0]

    prediction_file = open(infile, 'r')
    for data in prediction_file:
        fields = data.strip().split()
        if mapper_swiss.has_key(fields[0]):
            print >> outfile_handle, mapper_swiss[fields[0]] + '\t' + fields[1] + '\t' + fields[2]
        elif mapper_uni.has_key(fields[0]):
            print >> outfile_handle, mapper_uni[fields[0]] + '\t' + fields[1] + '\t' + fields[2]
        else:
            print >> outfile_handle, fields[0] + '\t' + fields[1] + '\t' + fields[2]
    
    prediction_file.close()
    outfile_handle.close()
    db1.clear()
    mapper_swiss.clear()
    mapper_uni.clear()
    
    return outfile_name

def mapper_bench(infile):
    
    db1 = defaultdict()
    mapper_swiss = defaultdict()
    mapper_uni = defaultdict()

    outfile_name = infile + '.id_mapped'
    
    universal_map_file = open('idmapping_selected.tab', 'r')

    outfile_handle = open(outfile_name, 'w')

    prediction_file = open(infile, 'r')
    for data in prediction_file:
        fields = data.strip().split()
        db1[fields[0]] = '1'

    prediction_file.close()

    for protein in universal_map_file:
        cols = protein.strip().split()
        if db1.has_key(cols[0]):
            mapper_uni[cols[0]] = cols[0]
        
        elif db1.has_key(cols[1]):
            mapper_swiss[cols[1]] = cols[0]

    prediction_file = open(infile, 'r')
    for data in prediction_file:
        fields = data.strip().split()
        if mapper_swiss.has_key(fields[0]):
            print >> outfile_handle, mapper_swiss[fields[0]] + '\t' + fields[1]
        elif mapper_uni.has_key(fields[0]):
            print >> outfile_handle, mapper_uni[fields[0]] + '\t' + fields[1]
        else:
            print >> outfile_handle, fields[0] + '\t' + fields[1]
    

    prediction_file.close()
    outfile_handle.close()
    db1.clear()
    mapper_swiss.clear()
    mapper_uni.clear()
    
    return outfile_name

if __name__ == "__main__":

    infile = sys.argv[1]
    mapper(infile)
