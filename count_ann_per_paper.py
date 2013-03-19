#!/usr/bin/python

import os
import sys
from collections import defaultdict

def count(infile, EEC=set([]), ann_conf_filter=0, paper_conf_filter=0):
    paper_conf = defaultdict(lambda:defaultdict(set))
    ann_conf = defaultdict(lambda:defaultdict(set))
    infile_handle = open(infile, 'r')
    
    for line in infile_handle:
        if line.startswith('!gaf-version'):
            continue
        fields = line.strip().split('\t')
        if fields[5] != '':
            paper_id = fields[5].split(':')[1]
        
        if (not EEC) or (fields[6] in EEC):
            if ann_conf_filter == 1 and paper_conf_filter == 1:
                ann_conf[fields[1]][fields[4]].add(str(paper_id))
                paper_conf[paper_id][fields[4]] = 1
            elif ann_conf_filter == 1 and paper_conf_filter == 0:
                ann_conf[fields[1]][fields[4]].add(str(paper_id))
            elif paper_conf_filter == 1 and ann_conf_filter == 0:
                paper_conf[paper_id][fields[4]] = 1
    
    infile_handle.close()
    return ann_conf, paper_conf


if __name__ == '__main__':
    infile = sys.argv[1]
    paper_term = count(infile, EEC)
