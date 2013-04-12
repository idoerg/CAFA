#!/usr/bin/env python

import os
import sys
from collections import defaultdict

def createPred(pred_file, ontology=set(['F', 'P', 'C'])):

    go_mfo = defaultdict()
    go_bpo = defaultdict()
    go_cco = defaultdict()
    pred_annotation_mfo = defaultdict(lambda:defaultdict(lambda:set()))
    pred_annotation_bpo = defaultdict(lambda:defaultdict(lambda:set()))
    pred_annotation_cco = defaultdict(lambda:defaultdict(lambda:set()))

    print "Creating final prediction dataset...."

    if 'F' in ontology :
        mfo_file_handle = open('list_of_molecular_function_terms.txt','r')
        for data in mfo_file_handle:
            data = data.strip()
            go_mfo[data] = 1
        
        file_handle = open(pred_file, 'r')
        for lines in file_handle:
            fields = lines.strip().split()
            if go_mfo.has_key(fields[1]):
                pred_annotation_mfo[fields[2]][fields[0]].add(fields[1])

    if 'P' in ontology:
        bpo_file_handle = open('list_of_biological_process_terms.txt','r')
        for data in bpo_file_handle:
            data = data.strip()
            go_bpo[data] = 1
        
        file_handle = open(pred_file, 'r')
        for lines in file_handle:
            fields = lines.strip().split('\t')
            if go_bpo.has_key(fields[1]):
                pred_annotation_bpo[fields[2]][fields[0]].add(fields[1])

    if 'C' in ontology:
        cco_file_handle = open('list_of_celular_component_terms.txt','r')
        for data in cco_file_handle:
            data = data.strip()
            go_cco[data] = 1
        
        file_handle = open(pred_file, 'r')
        for lines in file_handle:
            fields = lines.strip().split('\t')
            if go_cco.has_key(fields[1]):
                pred_annotation_cco[fields[2]][fields[0]].add(fields[1])

    return pred_annotation_mfo, pred_annotation_bpo, pred_annotation_cco

def createBench(exp_file, ontology=set(['F', 'P', 'C'])):

    go_mfo = defaultdict()
    go_bpo = defaultdict()
    go_cco = defaultdict()
    exp_annotation_mfo = defaultdict(lambda:set())
    exp_annotation_bpo = defaultdict(lambda:set())
    exp_annotation_cco = defaultdict(lambda:set())
    unique_prots_mfo = defaultdict()
    unique_prots_bpo = defaultdict()
    unique_prots_cco = defaultdict()

    print "Creating final benchmark dataset...."

    if 'F' in ontology :
        mfo_file_handle = open('list_of_molecular_function_terms.txt','r')
        for data in mfo_file_handle:
            data = data.strip()
            go_mfo[data] = 1
        
        file_handle = open(exp_file, 'r')
        for lines in file_handle:
            fields = lines.strip().split()
            if go_mfo.has_key(fields[1]):
                unique_prots_mfo[fields[0]] = 1
                exp_annotation_mfo[fields[0]].add(fields[1])

    if 'P' in ontology:
        bpo_file_handle = open('list_of_biological_process_terms.txt','r')
        for data in bpo_file_handle:
            data = data.strip()
            go_bpo[data] = 1
        
        file_handle = open(exp_file, 'r')
        for lines in file_handle:
            fields = lines.strip().split('\t')
            if go_bpo.has_key(fields[1]):
                unique_prots_bpo[fields[0]] = 1
                exp_annotation_bpo[fields[0]].add(fields[1])

    if 'C' in ontology:
        cco_file_handle = open('list_of_celular_component_terms.txt','r')
        for data in cco_file_handle:
            data = data.strip()
            go_cco[data] = 1
        
        file_handle = open(exp_file, 'r')
        for lines in file_handle:
            fields = lines.strip().split('\t')
            if go_cco.has_key(fields[1]):
                unique_prots_cco[fields[0]] = 1
                exp_annotation_cco[fields[0]].add(fields[1])

    return exp_annotation_mfo, exp_annotation_bpo, exp_annotation_cco, unique_prots_mfo, unique_prots_bpo, unique_prots_cco


if __name__ == '__main__':
    pred_file = sys.argv[1]
    ont = set(['F', 'P', 'C'])
    create(pred_file, ont)
