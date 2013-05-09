#!/usr/bin/env python

import os
import sys
import re
from collections import defaultdict
import urllib
import subprocess

def down(infile, host_url, unique_proteins):
    outfile = infile + '.sequence.fasta'
    outfile_handle = open(outfile, 'a')

    NumOfProts = len(unique_proteins)

    if NumOfProts > 500 :
        response = raw_input('Downloading ' + str(NumOfProts) + ' sequences might take a while. Type y to continue or n to exit : ')
        if response == 'y':
            print 'Creating fasta file of benchmark protein sequences.'
            for prots in unique_proteins:
                download_cmd = 'http://' + host_url + '?query=id:' + prots + '&format=fasta'
                urllib.urlretrieve(download_cmd, 'protein_sequence.fasta')
                subprocess.call(['cat -s protein_sequence.fasta ' + '>> ' + outfile], shell=True)
            os.remove('protein_sequence.fasta')

    elif NumOfProts > 0:
        print 'Creating fasta file of benchmark protein sequences.'
        for prots in unique_proteins:
            download_cmd = 'http://' + host_url + '?query=id:' + prots + '&format=fasta'
            urllib.urlretrieve(download_cmd, 'protein_sequence.fasta')
            subprocess.call(['cat -s protein_sequence.fasta ' + '>> ' + outfile], shell=True)
        os.remove('protein_sequence.fasta')


if __name__ == '__main__':
    infile = sys.argv[1]
    down(infile, host_url='http://', unique_proteins=defaultdict())
