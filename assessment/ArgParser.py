#!/usr/bin/python

import os
import sys
from collections import defaultdict
import re
import argparse


def parse(parser):
    args,unknown = parser.parse_known_args()
    if len(unknown) > 0:
        print "Invalid arguments."
        print parser.parse_args(['--help'])

    user_dict = defaultdict()

    if args.prediction:
        if len(args.prediction) > 1:
            print 'Multiple files have been provided as input\n'
            sys.exit(1)
        else:
            pred_file = args.prediction[0]
    else:
        print "Missing prediction file.\n"
        print parser.parse_args(['--help'])
        
    if args.benchmark:
        if len(args.benchmark) > 1:
            print 'Multiple files have been provided as input\n'
            sys.exit(1)
        else:
            bench_file = args.benchmark[0]
    else:
        print "Missing benchmark file. You can use the CAFA B.C tool to create a benchmark for your dataset.\n"
        print parser.parse_args(['--help'])

    
    if args.ontology:
        user_ontology = set(args.ontology)
        if 'all' in user_ontology:
            user_ontology = set(['F', 'P', 'C'])
    else:
        user_ontology = set(['F', 'P', 'C'])

    if args.prop:
        prop_status = args.prop
    else:
        prop_status = 'F'

    user_dict = {'pred_file' : pred_file,
                 'bench_file' : bench_file,
                 'user_ontology' : user_ontology,
                 'prop_status' : prop_status
                 }

    return user_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='assess_prediction.py',description='Asseess the predictions produced through different prediction methods')

    parser.add_argument('-P', '--prediction',action='store',help='Specifies the path to a file containing predictions from a specific method. The file needs to follow the required format to be accepted by the software.')
    parser.add_argument('-B', '--benchmark',action='store' ,help='Specifies the path to a file containing true experimental validations for the target proteins. This can be a simple tab delimited file with 2 columns, the first column is the protein identifier and second column contains the GO term.')
    parser.add_argument('-N', '--ontology',action='store',nargs='*',default=['all'],help='Provide a choice as to what type of ontology would the user like to assess. In the default event, assessment of all ontologies will be provided')
    parser.add_argument('-R', '--prop',action='store',default='F',help='Mention whether the input prediction file has predictions propagated to the root or not. By default, it is assumed that the predictions are unpropagated.Set to False')
    parse(parser)
