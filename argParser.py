#!/usr/bin/python -W

import os
import sys
import argparse
from collections import defaultdict
import warnings

def parse(args):

    t1_file = ''
    t2_file = ''

    user_dict = defaultdict()

    if args.organism:
        user_ORG = set(args.organism)
        if 'all' in user_ORG:
            user_ORG = set()

    if args.ontology:
        user_ONT = set(args.ontology)
        if 'all' in user_ONT:
            user_ONT = set()

    if args.evidence:
        user_EVI = set(args.evidence)
        if 'all' in user_EVI:
            user_EVI = set()

    if args.cafa:
        user_mode = args.cafa
        
    if args.source:
        user_source = set(args.source)
        if 'all' in user_source:
            user_source = set()

    if args.t1:
        t1_file = args.t1

    if args.t2:
        t2_file = args.t2

    if t1_file == '' or t2_file == '':
        print 'Missing an input file'
        sys.exit(1)

    if t1_file == t2_file:
        warnings.warn('Both input files are from the same time point. This will not create a valid benchmark')
        
    
    user_dict = {'user_ORG' : user_ORG,
                 'user_ONT' : user_ONT,
                 'user_EVI' : user_EVI,
                 'user_mode': user_mode,
                 'user_source' : user_source,
                 't1' : t1_file,
                 't2' : t2_file
                 }

    return user_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='ArgParser',description='Parses user input arguments')
    parser.add_argument('-O','--organism',nargs='+', default=['all'],help='Specifies a set of organisms (multiple organisms to be separated by space) whose proteins will be considered for benchmarking. Default is all organisms')
    parser.add_argument('-N','--ontology',nargs='+', default=['all'],help='Specifies the set of ontologies(multiple ontologies to be separated by space) to be used. By default, all 3 ontologies will be used. Default is all 3 ontologies')
    parser.add_argument('-V','--evidence',nargs='+', default=['all'],help='Specifies the evidence codes to be considered (multiple codes separated by space). By default, all experimentally validated evidence codes (as per GO standards) will be considered. Default is all experimental evidence codes')
    parser.add_argument('-C','--cafa', default='False' ,help='Specifies whether a user is a CAFA participant or not (True/False). Default is False')
    parser.add_argument('-I1', '--t1',action='store',help='Specifies the path to a Target file (either CAFA Targets File or any other. If not specified, defaults to None')
    parser.add_argument('-I2', '--t2',action='store' ,help='Specifies either the path to a file with experimental evidence codes or mentions a version in MM_YYYY format (for eg: Dec_2006)to be downloaded.If not specified, defaults to None')
    parser.add_argument('-S', '--source',action='store' ,nargs='+',default=['all'],help='Provides filter options on the datbaases that assigned aparticular annotation. If not specified, the program returns results from all sources.')
    args = parser.parse_args()
    parsed_args = parse(args)

    
