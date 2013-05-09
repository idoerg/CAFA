#!/usr/bin/python

import os
import sys
import re
from matplotlib import pyplot as py
from collections import defaultdict
import subprocess
import urllib

def plot_stats(benchmark_file):
    x_val = []
    y_val = []
    dist_ontology = defaultdict(lambda:defaultdict())
    unique_proteins_new = {}
    unique_proteins = {}
    pname = benchmark_file + '.png'
    xTickNames = []
    index = 0
    response = None
    fig = py.figure()
    py.ylabel('Frequency')

    infile_handle = open(benchmark_file, 'r')
    for lines in infile_handle:
        fields = lines.strip().split('\t')
        unique_proteins[fields[0]] = 1
        if fields[-1] == 'N':
            unique_proteins_new[fields[0]] = 1
        dist_ontology[fields[2]][fields[0]] = 1

    infile_handle.close()
    
    x = range(len(dist_ontology))
    for key1 in dist_ontology:
        x_val.append(index)
        y_val.append(len(dist_ontology[key1]))
        if key1 == 'F':
            xTickNames.append('Molecular_Function')
        elif key1 == 'P':
                xTickNames.append('Biological_Process')
        elif key1 == 'C':
            xTickNames.append('Cellular_Component')
        index = index + 1
    py.bar(x_val,y_val,facecolor='red', width=0.25, align='center')
    py.xticks(x, xTickNames)

    fig.autofmt_xdate()
    fig.savefig(pname.strip())

    dist_ontology.clear()

    return unique_proteins_new, unique_proteins

if __name__ == '__main__' :
    infile = sys.argv[1]
    plot_stats(infile)
