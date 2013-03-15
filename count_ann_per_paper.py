#!/usr/bin/python

import os
import sys
from collections import defaultdict

def count(infile, EEC=set([])):
    paper_term = defaultdict(lambda:defaultdict(set))
    infile_handle = open(infile, 'r')
    
    for line in infile_handle:
        if line.startswith('!gaf-version'):
            continue
        fields = line.strip().split('\t')
        if fields[5] != '':
            paper_id = fields[5].split(':')[1]
        else:
            paper_id = ' '
        if (not EEC) or (fields[6] in EEC):
            paper_term[paper_id][fields[4]] = 1
    
    infile_handle.close()
    return paper_term


if __name__ == '__main__':
    infile = sys.argv[1]
    paper_term = count(infile, EEC)
