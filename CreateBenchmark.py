#!/usr/bin/env python

import sys
import os
import re
from collections import defaultdict

'''
   This script creates the final benchmark set of proteins.
   There are 2 methods in this module suited towards whether the benchmark
   program is run in CAFA or non-CAFA mode.

   The script extracts proteins that were exclusively IEA in a particular ontology
   in time t1 and obtained experimental evidence for that ontology in t2.

   It also extracts those proteins that had some experimental evidence for a 
   particular ontology in t1 and gained function in the same ontology at time
   point t2.

   The final benchmark file is tab delimited with 4 columns. The last column
   mentions either a N or O. N stands for all novel annotations that a protein
   gained over the time period specified and falls under the 2 categories 
   mentioned above. The O stands for old annotations. So, proteins having 
   annotations with experimental evidence in t1 come under this set.

   Ideally, for the CAFA competition, only novel annotations are considered.
   But if a user wants a complete set of annotations that a protein might have,
   he would need annotations labelled both N and O.
'''
def parse(t1_iea, t1_exp, t2_exp, iea_default=set([]), EEC_default=set([])):
    t2_dict_mfo = defaultdict(lambda:set())
    t2_dict_bpo = defaultdict(lambda:set())
    t2_dict_cco = defaultdict(lambda:set())
    t1_exp_dict = defaultdict(lambda:defaultdict(lambda:set()))

    for lines in t1_exp:
        fields = lines.strip().split('\t')
        t1_exp_dict[fields[1]][fields[8]].add(fields[4])

    t1_exp.close()

    t2_handle = open(t2_exp, 'r')

    for lines in t2_handle:
        cols = lines.strip().split('\t')
        if len(cols) < 15:
            continue
        if cols[8] == 'F':
            t2_dict_mfo[cols[1]].add(cols[4])
        elif cols[8] == 'P':
            t2_dict_bpo[cols[1]].add(cols[4])
        elif cols[8] == 'C':
            t2_dict_cco[cols[1]].add(cols[4])

    t2_handle.close()

    outfile = open(t2_exp + '_bench.txt' , 'w')

    print 'Creating benchmark set.....'

    for lines in t1_iea:
        fields = lines.strip().split('\t')
        if fields[6] in iea_default:
            if t1_exp_dict.has_key(fields[1]):
                if not t1_exp_dict[fields[1]].has_key(fields[8]):
                    if fields[8] == 'F':
                        for term in t2_dict_mfo[fields[1]]:
                            print >> outfile, str(fields[1]) + '\t' + str(term) + \
                                '\t' + 'F' + '\t' + 'N'
                    elif fields[8] == 'P':
                        for term in t2_dict_bpo[fields[1]]:
                            print >> outfile, str(fields[1]) + '\t' + str(term) + \
                                '\t' + 'P' + '\t' + 'N'
                    elif fields[8] == 'C':
                        for term in t2_dict_cco[fields[1]]:
                            print >> outfile, str(fields[1]) + '\t' + str(term) + \
                                '\t' + 'C' + '\t' + 'N'

            else:
                if t2_dict_mfo.has_key(fields[1]):
                    for term in t2_dict_mfo[fields[1]]:
                        print >> outfile, str(fields[1]) + '\t' + str(term) + \
                            '\t' + 'F' + '\t' + 'N'
                if t2_dict_bpo.has_key(fields[1]):
                    for term in t2_dict_bpo[fields[1]]:
                        print >> outfile, str(fields[1]) + '\t' + str(term) + \
                            '\t' + 'P' + '\t' + 'N'
                if t2_dict_cco.has_key(fields[1]):
                    for term in t2_dict_cco[fields[1]]:
                        print >> outfile, str(fields[1]) + '\t' + str(term) + \
                            '\t' + 'C' + '\t' + 'N'


    t2_dict_mfo.clear()
    t2_dict_bpo.clear()
    t2_dict_cco.clear()
    t1_iea.close()

    t2_handle = open(t2_exp, 'r')

    for lines in t2_handle:
        fields = lines.strip().split('\t')
        if len(fields) < 15:
            continue
        if t1_exp_dict.has_key(fields[1]):
            if t1_exp_dict[fields[1]].has_key(fields[8]):
                if not fields[4] in t1_exp_dict[fields[1]][fields[8]]:
                    print >> outfile, fields[1] + '\t' + fields[4] + \
                        '\t' + fields[8] + '\t' + 'N'
                else:
                    print >> outfile, fields[1] + '\t' + fields[4] + \
                        '\t' + fields[8] + '\t' + 'O'
            else:
                print >> outfile, fields[1] + '\t' + fields[4] + \
                    '\t' + fields[8] + '\t' + 'N'

    t2_handle.close()
    outfile.close()
    t1_exp_dict.clear()

def parse_cafa(t2_file, t1_file):

    t1_dict = defaultdict()

    t1_file_handle = open(t1_file, 'r')

    for lines in t1_file_handle:
        fields = lines.strip().split('\t')
        t1_dict[fields[1]] = 1

    t1_file_handle.close()
    
    outfile = open(t2_file + '_bench.txt' , 'w')

    print 'Creating benchmark set.....'

    t2_file_handle = open(t2_file, 'r')
    
    for lines in t2_file_handle:
        fields = lines.strip().split('\t')
        swiss_id = fields[10].split('|')[0]
        if t1_dict.has_key(fields[1]):
            print >> outfile, fields[1] + '\t' + fields[4] + \
                '\t' + fields[8] + '\t' + 'N'
        elif t1_dict.has_key(swiss_id):
            print >> outfile, fields[1] + '\t' + fields[4] + \
                '\t' + fields[8] + '\t' + 'N'

    t1_dict.clear()
    t2_file_handle.close()

if __name__ == '__main__':
    exp_file = sys.argv[1]
    iea_file = sys.argv[2]
    parse(exp_file, iea_file, ontos=set(['F', 'P', 'C']))
