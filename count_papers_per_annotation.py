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
        if (not EEC) or (fields[6] in EEC):
            paper_term[fields[1]][fields[4]].add(str(fields[5]))
    
    infile_handle.close()
    return paper_term


if __name__ == '__main__':
    infile = sys.argv[1]
    paper_term = count_papers(infile, EEC)
