#!/usr/bin/env python

import sys
import os
import re
from collections import defaultdict


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
                            print >> outfile, str(fields[1]) + '\t' + str(term) + '\t' + 'F' + '\t' + 'N'
                    elif fields[8] == 'P':
                        for term in t2_dict_bpo[fields[1]]:
                            print >> outfile, str(fields[1]) + '\t' + str(term) + '\t' + 'P' + '\t' + 'N'
                    elif fields[8] == 'C':
                        for term in t2_dict_cco[fields[1]]:
                            print >> outfile, str(fields[1]) + '\t' + str(term) + '\t' + 'C' + '\t' + 'N'

            else:
                if t2_dict_mfo.has_key(fields[1]):
                    for term in t2_dict_mfo[fields[1]]:
                        print >> outfile, str(fields[1]) + '\t' + str(term) + '\t' + 'F' + '\t' + 'N'
                if t2_dict_bpo.has_key(fields[1]):
                    for term in t2_dict_bpo[fields[1]]:
                        print >> outfile, str(fields[1]) + '\t' + str(term) + '\t' + 'P' + '\t' + 'N'
                if t2_dict_cco.has_key(fields[1]):
                    for term in t2_dict_cco[fields[1]]:
                        print >> outfile, str(fields[1]) + '\t' + str(term) + '\t' + 'C' + '\t' + 'N'


    t2_dict_mfo.clear()
    t2_dict_bpo.clear()
    t2_dict_cco.clear()
    t1_iea.close()

    t2_handle = open(t2_exp, 'r')
    #prots = defaultdict()

    for lines in t2_handle:
        fields = lines.strip().split('\t')
        if t1_exp_dict.has_key(fields[1]):
            if t1_exp_dict[fields[1]].has_key(fields[8]):
                if not fields[4] in t1_exp_dict[fields[1]][fields[8]]:
                    #prots[fields[1]] = 1
                    print >> outfile, fields[1] + '\t' + fields[4] + '\t' + fields[8] + '\t' + 'N'
                else:
                    #if prots.has_key(fields[1]):
                    print >> outfile, fields[1] + '\t' + fields[4] + '\t' + fields[8] + '\t' + 'O'
            else:
                print >> outfile, fields[1] + '\t' + fields[4] + '\t' + fields[8] + '\t' + 'N'

    t2_handle.close()
    outfile.close()
    t1_exp_dict.clear()
    #prots.clear()

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
        fields = lines.strip().split()
        if t1_dict.has_key(fields[0]):
            print >> outfile, fields[0] + '\t' + fields[2] + '\t' + fields[1] + '\t' + 'N'
        elif t1_dict.has_key(fields[-1]):
            print >> outfile, fields[0] + '\t' + fields[2] + '\t' + fields[1] + '\t' + 'N'

    t1_dict.clear()
    t2_file_handle.close()

    '''
    #map_table = open('mapping_table.txt','r')
    #map_dict = defaultdict()

    #for mapper in map_table:
     #   [swiss_id, uniprot_id] = mapper.strip().split('\t')
      #  map_dict[swiss_id] = uniprot_id


    t2_dict_mfo = defaultdict(lambda:set())
    t2_dict_bpo = defaultdict(lambda:set())
    t2_dict_cco = defaultdict(lambda:set())

    t2_handle = open(t2_file, 'r')

    for lines in t2_handle:
        fields = lines.strip().split('\t')
        if fields[1] == 'F':
            t2_dict_mfo[fields[0]].add(fields[2])
            t2_dict_mfo[fields[-1]].add(fields[2])
        elif fields[1] == 'P':
            t2_dict_bpo[fields[0]].add(fields[2])
            t2_dict_bpo[fields[-1]].add(fields[2])
        elif fields[1] == 'C':
            t2_dict_cco[fields[0]].add(fields[2])
            t2_dict_cco[fields[-1]].add(fields[2])


    t2_handle.close()

    outfile = open(t2_file + '_bench.txt' , 'w')

    print 'Creating benchmark set.....'

    t1_handle = open(t1_file, 'r')

    for lines in t1_handle:
        fields = lines.strip().split()
        
        #if map_dict.has_key(lines):
         #   uni_id = map_dict[lines]
        #else:
         #   uni_id = lines
        if t2_dict_mfo.has_key(fields[0]):
            for term in t2_dict_mfo[fields[0]]:
                print >> outfile, str(fields[0]) + '\t' + 'F' + '\t' + str(term) + '\t' + fields[1]

        elif t2_dict_mfo.has_key(fields[1]):
            for term in t2_dict_mfo[fields[1]]:
                print >> outfile, str(fields[0]) + '\t' + 'F' + '\t' + str(term) + '\t' + fields[1]

        if t2_dict_bpo.has_key(fields[0]):
            for term in t2_dict_bpo[fields[0]]:
                print >> outfile, str(fields[0]) + '\t' + 'P' + '\t' + str(term) + '\t' + fields[1]

        elif t2_dict_bpo.has_key(fields[1]):
            for term in t2_dict_bpo[fields[1]]:
                print >> outfile, str(fields[0]) + '\t' + 'P' + '\t' + str(term) + '\t' + fields[1]

        if t2_dict_cco.has_key(fields[0]):
            for term in t2_dict_cco[fields[0]]:
                print >> outfile, str(fields[0]) + '\t' + 'C' + '\t' + str(term) + '\t' + fields[1]

        elif t2_dict_cco.has_key(fields[1]):
            for term in t2_dict_cco[fields[1]]:
                print >> outfile, str(fields[0]) + '\t' + 'C' + '\t' + str(term) + '\t' + fields[1]

      '''

if __name__ == '__main__':
    exp_file = sys.argv[1]
    iea_file = sys.argv[2]
    parse(exp_file, iea_file, ontos=set(['F', 'P', 'C']))
