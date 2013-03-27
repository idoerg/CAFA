#!/usr/bin/python -W

import os
import sys
import argparse
from collections import defaultdict
import logging


def parse(parser):

    args, unknown = parser.parse_known_args()

    if len(unknown) > 0:
        print "Invalid Arguments"
        print parser.parse_args(['--help'])

    t1_file = ''
    t2_file = ''

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    user_dict = defaultdict()

    print 'Following are the options specified by the user : '

    sys.stdout.write( "Organisms : ")
    if args.organism:
        args.organism = [x.capitalize() for x in args.organism]
        [sys.stdout.write(x + ' ') for x in args.organism]
    
        user_ORG = set(args.organism)
        if 'All' in user_ORG:
            user_ORG = set()
    else:
        user_ORG = set([])
    
    sys.stdout.write('\n')

    sys.stdout.write("Ontology : ")

    if args.ontology:
        args.ontology = [x.upper() for x in args.ontology]
        [sys.stdout.write(x + ' ') for x in args.ontology]

        user_ONT = set(args.ontology)
        if 'ALL' in user_ONT:
            user_ONT = set([])
    else:
        user_ONT = set([])

    sys.stdout.write('\n')
    sys.stdout.write("Evidence : ")

    if args.evidence:
        args.evidence = [x.upper() for x in args.evidence]
        [sys.stdout.write(x + ' ') for x in args.evidence]

        user_EVI = set(args.evidence)
        if 'ALL' in user_EVI:
            user_EVI = set([])
    else:
        user_EVI = set([])

    sys.stdout.write('\n')
    sys.stdout.write("CafaMode : ")


    if args.cafa:
        user_mode = args.cafa
    else:
        user_mode = 'F'
        
    sys.stdout.write(user_mode + '\n')
    sys.stdout.write("SourceDB : ")

    if args.source:
        args.source = [x.upper() for x in args.source]
        [sys.stdout.write(x + ' ') for x in args.source]

        user_source = set(args.source)
        if 'ALL' in user_source:
            user_source = set([])
    else:
        user_source = set([])

    sys.stdout.write("\n")

    if args.i1:
        sys.stdout.write("T1 : ")
        if len(args.i1) > 1:
            print('Multiple inputs have been provided for t1 file')
            sys.exit(1)
        else:
            t1_file = args.i1[0]
    else:
        print parser.parse_args(['--help'])
    
    sys.stdout.write(t1_file + '\n')

    if args.i2:
        sys.stdout.write("T2 : ")
        if len(args.i2) > 1:
            print('Multiple inputs have been provided for t2 file')
            sys.exit(1)
        else:
            t2_file = args.i2[0]
    else:
        print parser.parse_args(['--help'])

    sys.stdout.write(t2_file + '\n')
    sys.stdout.write('*************************************************************************************\n')

    if t1_file == t2_file:
        logging.warning('Both input files are from the same time point. This will not create a valid benchmark')
        
    
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

    
