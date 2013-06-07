#!/usr/bin/env python

import os
import sys
from collections import defaultdict

def create(infile1, infile2, benchmark_filename, targetType):

    exp_prot = defaultdict(lambda:defaultdict())
    final_targets = defaultdict(lambda:defaultdict())

    infile2_handle = open(infile2, 'r')

    for lines in infile2_handle:
        fields = lines.strip('\n').split('\t')
        if len(fields) < 15:
            continue
        exp_prot[fields[1]][fields[8]] = 1


    outfile = open(benchmark_filename, 'w')

    infile1_handle = open(infile1, 'r')

    print "Target generation in process"
    if targetType == 0:
        for lines in infile1_handle:
            fields = lines.strip('\n').split('\t')
            taxid = fields[12].split(':')[1]
            if len(fields) < 15:
                continue
            if exp_prot.has_key(fields[1]):
                if exp_prot[fields[1]].has_key(fields[8]):
                    continue
                else:
                    print >> outfile, fields[1] + '\t' + fields[8] + '\t' + taxid
            else:
                print >> outfile, fields[1] + '\t' + fields[8] + '\t' + taxid

    exp_prot.clear()
    

if __name__ == '__main__':
    create()
