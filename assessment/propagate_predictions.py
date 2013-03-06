#!/usr/bin/python

import re
import sys
import os
from collections import defaultdict

def main():
    input_file = sys.argv[1]

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

    outfile_name = input_file.split('_')[0] + '_prediction_propagated.txt'
    outfile_handle = open(outfile_name,'w')

    pred_file_handle = open(input_file, 'r')
    for data in pred_file_handle:
        fields = re.sub(r'\n','',data).split(' ')
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


if __name__ == "__main__":
    main()

'''
pred_file_handle = open(input_file, 'r')
for data in pred_file_handle:
    fields = re.sub(r'\n','',data).split(' ')
    #print >> outfile, fields[0] + '\t' + fields[1] + '\t' + fields[2]
    if not prot_term[fields[0]].has_key(fields[1]):
        prot_term[fields[0]][fields[1]] = fields[2]
    if go_tree.has_key(fields[1]):
        for term in go_tree[fields[1]]:
            if not prot_term[fields[0]].has_key(term):
                #print >> outfile, fields[0] + '\t' + term + '\t' + fields[2]
                prot_term[fields[0]][term] = fields[2]
            elif fields[2] > prot_term[fields[0]][term]:
                prot_term[fields[0]][term] = fields[2]

'''
