#!/usr/bin/python

import sys
import os
import re
from collections import defaultdict

def parse(t2, t1, ontos):
    t2_dict_mfo = defaultdict(lambda:set())
    t2_dict_bpo = defaultdict(lambda:set())
    t2_dict_cco = defaultdict(lambda:set())
    t2_handle = open(t2, 'r')

    for lines in t2_handle:
        fields = lines.strip().split('\t')
        if fields[1] == 'F':
            t2_dict_mfo[fields[0]].add(fields[2])
        elif fields[1] == 'P':
            t2_dict_bpo[fields[0]].add(fields[2])
        elif fields[1] == 'C':
            t2_dict_cco[fields[0]].add(fields[2])
            

    t2_handle.close()

    bench_dict = defaultdict(lambda:defaultdict())

    outfile = open(t2 + '_bench.txt' , 'w')

    print 'Creating benchmark set.....'

    t1_handle = open(t1, 'r')
    for lines in t1_handle:
        counter = 0
        fields = lines.strip().split('\t')

        if fields[2] == 'all_excl':
            if t2_dict_mfo.has_key(fields[0]):
                for term in t2_dict_mfo[fields[0]]:
                    print >> outfile, str(fields[0]) + '\t' + 'F' + '\t' + str(term)
                    
            if t2_dict_bpo.has_key(fields[0]):
                for term in t2_dict_bpo[fields[0]]:
                    print >> outfile, str(fields[0]) + '\t' + 'P' + '\t' + str(term)
                    
            if t2_dict_cco.has_key(fields[0]):
                for term in t2_dict_cco[fields[0]]:
                    print >> outfile, str(fields[0]) + '\t' + 'C' + '\t' + str(term)
                    
        elif fields[2] == 'part_excl':
            if fields[1] == 'F':
                if t2_dict_mfo.has_key(fields[0]):
                    for term in t2_dict_mfo[fields[0]]:
                        print >> outfile, str(fields[0]) + '\t' + str(fields[1]) + '\t' + str(term)
                        
            elif fields[1] == 'P':
                if t2_dict_bpo.has_key(fields[0]):
                    for term in t2_dict_bpo[fields[0]]:
                        print >> outfile, str(fields[0]) + '\t' + str(fields[1]) + '\t' + str(term)
                
            elif fields[1] == 'C':
                if t2_dict_cco.has_key(fields[0]):
                    for term in t2_dict_cco[fields[0]]:
                        print >> outfile, str(fields[0]) + '\t' + str(fields[1]) + '\t' + str(term)


    bench_dict.clear()

def parse_cafa(t2_file, t1_file):

    map_table = open('mapping_table.txt','r')
    map_dict = defaultdict()

    for mapper in map_table:
        [swiss_id, uniprot_id] = mapper.strip().split('\t')
        map_dict[swiss_id] = uniprot_id


    t2_dict_mfo = defaultdict(lambda:set())
    t2_dict_bpo = defaultdict(lambda:set())
    t2_dict_cco = defaultdict(lambda:set())

    t2_handle = open(t2_file, 'r')

    for lines in t2_handle:
        fields = lines.strip().split('\t')
        if fields[1] == 'F':
            t2_dict_mfo[fields[0]].add(fields[2])
        elif fields[1] == 'P':
            t2_dict_bpo[fields[0]].add(fields[2])
        elif fields[1] == 'C':
            t2_dict_cco[fields[0]].add(fields[2])


    t2_handle.close()

    outfile = open(t2_file + '_bench.txt' , 'w')

    print 'Creating benchmark set.....'

    t1_handle = open(t1_file, 'r')

    for lines in t1_handle:
        lines.strip()
        if map_dict.has_key(lines):
            uni_id = map_dict[lines]
        else:
            uni_id = lines
        if t2_dict_mfo.has_key(uni_id):
            for term in t2_dict_mfo[uni_id]:
                print >> outfile, str(fields[0]) + '\t' + 'F' + '\t' + str(term)

        if t2_dict_bpo.has_key(uni_id):
            for term in t2_dict_bpo[uni_id]:
                print >> outfile, str(fields[0]) + '\t' + 'P' + '\t' + str(term)

        if t2_dict_cco.has_key(uni_id):
            for term in t2_dict_cco[uni_id]:
                print >> outfile, str(fields[0]) + '\t' + 'C' + '\t' + str(term)
    


if __name__ == '__main__':
    exp_file = sys.argv[1]
    iea_file = sys.argv[2]
    parse(exp_file, iea_file, ontos=set(['F', 'P', 'C']))
