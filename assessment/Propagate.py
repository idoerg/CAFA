#!/usr/bin/python

import re
import sys
import os
from collections import defaultdict

'''
    In the event that the user predictions and benchmark set are not
    propagated to contain all ancestral terms in the GO tree, this script
    will go ahead and do that and return a propagated prediction and
    benchmark file.

    Since the format of th eprediction and benchmark files are different,
    There are 2 methods to do the same kind of operation, one for the 
    prediction and the other for the benchmark file.

'''

def propagate_benchmark(bench_file):
    
    go_tree_handle = open('go_terms_with_all_ancestors_new.txt','r')                                                                        

    go_tree = defaultdict(lambda:defaultdict())                                                                                              

    for lines in go_tree_handle:                                                                                                            
        [child, ancestors] = re.sub(r'\n','',lines).split('\t')
        parents = ancestors.split(',')                                                                                                       
        for ancestor in parents:
            if ancestor == '':
                continue
            go_tree[child][ancestor] = 1

    prot_term = defaultdict(lambda:defaultdict())

    outfile_name = bench_file + '.propagated'
    outfile_handle = open(outfile_name,'w')

    print "Propagating benchmark data......."

    bench_file_handle = open(bench_file, 'r')
    for data in bench_file_handle:
        fields = data.strip().split()
        if not prot_term[fields[0]].has_key(fields[1]):
            prot_term[fields[0]][fields[1]] = 1
            print >> outfile_handle, fields[0] + '\t' + fields[1]
        if go_tree.has_key(fields[1]):
            for term in go_tree[fields[1]]:
                if not prot_term[fields[0]].has_key(term):
                    prot_term[fields[0]][term] = 1
                    print >> outfile_handle, fields[0] + '\t' + term


    go_tree.clear()
    prot_term.clear()

    return outfile_name
    
def propagate_prediction(input_file):

    go_tree_handle = open('go_terms_with_all_ancestors_new.txt','r')                                                                        

    go_tree = defaultdict(lambda:defaultdict())                                                                                              

    for lines in go_tree_handle:                                                                                                            
        [child, ancestors] = re.sub(r'\n','',lines).split('\t')                                                                             
        parents = ancestors.split(',')                                                                                                       
        for ancestor in parents:
            if ancestor == '':
                continue
            go_tree[child][ancestor] = 1

    prot_term = defaultdict(lambda:defaultdict())

    outfile_name = input_file + '.propagated'
    outfile_handle = open(outfile_name,'w')

    print "Propagating prediction data......."

    pred_file_handle = open(input_file, 'r')
    for data in pred_file_handle:
        fields = data.strip().split()
        if fields[0] == 'AUTHOR':
            continue
        if fields[0] == 'MODEL':
            continue
        if fields[0] == 'KEYWORDS':
            continue
        if re.match('^ACCURACY\s{1}',data):
            continue
        if re.match('^END', data):
            continue
        if data == ' ':
            continue

        if not prot_term[fields[0]].has_key(fields[1]):
            prot_term[fields[0]][fields[1]] = fields[2]
        if go_tree.has_key(fields[1]):
            for term in go_tree[fields[1]]:
                if not prot_term[fields[0]].has_key(term):
                    prot_term[fields[0]][term] = fields[2]
                elif fields[2] > prot_term[fields[0]][term]:
                    prot_term[fields[0]][term] = fields[2]


    for key1 in prot_term:
        for key2 in prot_term[key1]:
            print >> outfile_handle, key1 + '\t' + key2 + '\t' + prot_term[key1][key2]

    go_tree.clear()
    prot_term.clear()

    return outfile_name

if __name__ == "__main__":
    pred_file = sys.argv[1]
    propagate_prediction(pred_file)
