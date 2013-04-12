#!/usr/bin/python

import sys
import os
import re
from collections import defaultdict
import Mapping

def pred_filter(infile1, infile2):

    mapped_pred = Mapping.mapper_pred(infile1)
    mapped_bench = Mapping.mapper_bench(infile2)

    outfile_name = infile1 + '_pred_set.txt'
    outfile_handle = open(outfile_name, 'w')

    bench = defaultdict()

    b_file = open(mapped_bench,'r')
    for lines in b_file:
        fields = lines.strip().split()
        bench[fields[0]] = 1
        
    b_file.close()
    prot_ann = defaultdict()

    print "Filtering prediction data....\n"

    prediction_file = open(mapped_pred,'r')
    for data in prediction_file:
        fields = data.strip().split()
        if bench.has_key(fields[0]):
            print >> outfile_handle, fields[0] + '\t' + fields[1] + '\t' + fields[2]
            prot_ann[fields[0]] = 1

    prediction_file.close()
    prot_ann.clear()
    bench.clear()

    return outfile_name, mapped_bench


if __name__ == "__main__":
    infile1 = sys.argv[1]
    infile2 = sys.argv[2]
    pred_filter(infile1,infile2)

