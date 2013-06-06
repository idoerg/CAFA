#!/usr/bin/env python

import os
import sys
import re
from collections import defaultdict
import urllib
import subprocess

'''
   Given a set of proteins, this module connects to the uniprot api and
   downloads sequences for them. If the number of proteins exceeds 500,
   the program asks the user if they want to continue with the download
   process since it might take a while to complete downloading all.

   Finally creates an output fasta file of sequences.
'''
def down(infile, host_url, unique_proteins):
    outfile = infile + '.fasta'
    outfile_handle = open(outfile, 'a')

    NumOfProts = len(unique_proteins)

    if NumOfProts > 500 :
        response = raw_input('Downloading ' + str(NumOfProts) + \
                                 ' sequences might take a while. Type y to continue or n to exit : ')
        if response == 'y':
            print 'Creating fasta file of protein sequences.'
            for prots in unique_proteins:
                download_cmd = 'http://' + host_url + '?query=id:' + prots + '&format=fasta'
                urllib.urlretrieve(download_cmd, 'protein_sequence.fasta')
                subprocess.call(['cat -s protein_sequence.fasta ' + '>> ' + outfile], shell=True)
            os.remove('protein_sequence.fasta')

    elif NumOfProts > 0:
        print 'Creating fasta file of protein sequences.'
        for prots in unique_proteins:
            download_cmd = 'http://' + host_url + '?query=id:' + prots + '&format=fasta'
            urllib.urlretrieve(download_cmd, 'protein_sequence.fasta')
            subprocess.call(['cat -s protein_sequence.fasta ' + '>> ' + outfile], shell=True)
        os.remove('protein_sequence.fasta')


if __name__ == '__main__':
    infile = sys.argv[1]
    down(infile, host_url='http://', unique_proteins=defaultdict())
