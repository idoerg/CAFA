#!/usr/bin/python

import os
import sys
import re
from matplotlib import pyplot as py
from collections import defaultdict
#import ConfigParser
import subprocess

#Config = ConfigParser.ConfigParser()
#Config.read('config.rc')
#host_url = Config.get('SEQUENCE', 'BASE_URL')

def plot_stats(benchmark_file, host_url=''):
    x_val = []
    y_val = []
    dist_ontology = defaultdict(lambda:defaultdict())
    unique_proteins = defaultdict()
    pname = benchmark_file.replace('.txt', '.png')
    xTickNames = []
    index = 0
    response = ''
    fig = py.figure()
    py.ylabel('Frequency')

    infile_handle = open(benchmark_file, 'r')
    for lines in infile_handle:
        fields = lines.strip().split('\t')
        unique_proteins[fields[0]] = 1
        dist_ontology[fields[1]][fields[0]] = 1

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

    benchmark_file = benchmark_file.replace('_benchmark_set.txt', '')
    outfile = benchmark_file + '.sequence.fasta'

    NumOfProts = len(unique_proteins)

    if NumOfProts > 3000 :
        reponse = raw_input('Downloading ' + str(NumOfProts) + ' sequences may take a while. Type yes to continue or no to exit : ')
        if response == 'yes':
            print 'Creating fasta file of benchmark protein sequences.'
            for prots in unique_proteins:
                download_cmd = 'wget -qO- ' + host_url + prots + '.fasta ' + '>>' + outfile
                subprocess.call([download_cmd], shell=True)
        elif response == 'no':
            print 'Thank you for using the benchmark creator software.'
            sys.exit(1)
    else:
        for prots in unique_proteins:
            download_cmd = 'wget -qO- ' + host_url + prots + '.fasta ' + '>>' + outfile
            subprocess.call([download_cmd], shell=True)

if __name__ == '__main__' :
    infile = sys.argv[1]
    plot_stats(infile)
