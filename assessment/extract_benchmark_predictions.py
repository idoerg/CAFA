#!/usr/bin/python

import sys
import os
import re
from collections import defaultdict

def main():
    infile = sys.argv[1]
    outfile_name = infile.split('_')[0] + '_pred_set.txt'
    outfile_handle = open(outfile_name, 'w')

    bench = defaultdict()

    b_file = open('benchmark_propagated.txt','r')
    for lines in b_file:
        fields = re.sub(r'\n','',lines).split('\t')
        bench[fields[0]] = 1
        
    prot_ann = defaultdict()

    prediction_file = open(infile,'r')
    for data in prediction_file:
        corr_data = re.sub(r'\n','',data)
        fields = corr_data.split('\t')
        if bench.has_key(fields[0]):
            print >> outfile_handle, fields[0] + '\t' + fields[1] + '\t' + fields[2]
            prot_ann[fields[0]] = 1

if __name__ == "__main__":
    main()

