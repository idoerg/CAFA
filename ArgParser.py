#!/usr/bin/env python

import os
import sys
import argparse
import re
from collections import defaultdict

'''
   This script parses, verifies a bunch of user input parameters using argparse module.
   Finally creates a dictionary with all parameter values and returns it

'''
def extract_args(args):
    
    # This dictionary below contains the values of all arguments available to the program. 
    #If they have been passed, it will take the values passed. Else, will assume default values. 
    #If a new parameter is to be added to the program, it should be added into this dictionary
    args_dict = {}
    
    args_dict = {'Taxon_ID' : args.organism,
                 'Aspect' : args.ontology,
                 'Evidence' : args.evidence,
                 'Mode' : args.cafa,
                 'outfile' : args.output,
                 'Assigned_By' : args.source,
                 'Pubmed' : args.pubmed,
                 'Confidence' : args.confidence,
                 'Threshold' : args.threshold,
                 'Blacklist' : args.blacklist,
                 't1' : args.input1,
                 't2' : args.input2,
                 'Target' : args.targetType,
                 'Program' : args.mode
                 }

    print "*************************************************"
    if args_dict['Program'] == 'BC':
        print "Welcome to the Benchmark Creation tool !!!!!"
    else:
        print "Welcome to the Target Generation tool !!!!!"

    print "*************************************************\n"
    print 'Following is a list of user supplied inputs :\n'
    for arg in args_dict:
        print arg + ' : ' + str(args_dict[arg])
        
    print '*********************************************\n'

    return args_dict
    
def check_args(args_dict,parser):
    # This method checks the values for each of the arguments provided to look for inconsistent input
    # At the end, it creates a final dictionary of input argument values and gives it back to the main script

    user_dict = {}

    for arg in args_dict:
        if arg == 't1':
            if args_dict[arg] == None:
                print 'Missing T1 file\n'
                print parser.parse_args(['--help'])
            else:
                user_dict['t1'] = args_dict[arg]

        elif arg == 't2':
            if args_dict[arg] == None:
                print 'Missing T2 file\n'
                print parser.parse_args(['--help'])
            else:
                user_dict['t2'] = args_dict[arg]

        elif arg == 'Threshold':
            user_dict[arg] = args_dict[arg]
        elif arg == 'Confidence':
            user_dict[arg] = args_dict[arg]
            
        elif arg == 'outfile':
            user_dict[arg] = args_dict[arg]
        elif arg == 'Mode':
            user_dict[arg] = args_dict[arg]
        elif arg == 'Target':
            user_dict[arg] = args_dict[arg]
        elif arg == 'Program':
            user_dict[arg] = args_dict[arg]
            
        elif arg == 'Taxon_ID':
            if 'all' in args_dict[arg] or len(args_dict[arg]) == 0:
                user_dict[arg] = set([])
            else:
                args_dict[arg] = [x.capitalize() for x in args_dict[arg]]
                user_dict[arg] = set(args_dict[arg])
        else:
            if 'all' in args_dict[arg] or len(args_dict[arg]) == 0:
                user_dict[arg] = set([])
            else:
                args_dict[arg] = [x.upper() for x in args_dict[arg]]
                user_dict[arg] = set(args_dict[arg])

    if user_dict['t1'] == user_dict['t2']:
        print 'Both input files are from the same time point. This will not create a valid benchmark.\n'

    return user_dict


def parse(parser, ConfigParam=defaultdict()):
    args_dict = {}
    args, unknown = parser.parse_known_args()

    if len(unknown) > 0:
        print '\n*********************************'
        print "Invalid Arguments"
        print '*********************************\n'
        print parser.parse_args(['--help'])

    args_dict = extract_args(args)

    user_dict = check_args(args_dict,parser)

    return user_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='bm.py',description='Creates a set of benchmark proteins')
    parser.add_argument('-M', '--mode', default='BC', help='This option allows the user to run the program either as a Benchmark Creator or aTarget Generator. It takes in values of BC or TG. Default, if not provided is BC.')
    parser.add_argument('-G','--organism',nargs='*', default=['all'],help='Provides user a choice to specify a set of organisms (example:Saccharomyces cerevisiae or 7227) separated by space.Default is all.')
    parser.add_argument('-N','--ontology',nargs='*', default=['all'],help='Provides user a choice to specify a set of ontologies (F, P, C) separated by space. Default is all.')
    parser.add_argument('-V','--evidence',nargs='*', default=['all'],help='Provides user a choice to specify a set of GO experimental evidence codes (example: IPI, IDA, EXP) separated by space.Default is all.')
    parser.add_argument('-C','--cafa', default='F' ,help='Takes in either T or F. If specified as T, user needs to provide a CAFA targets file as input1. If F, program will take in a uniprot-goa file as input1. Default is F')
    parser.add_argument('-I1', '--input1', nargs='*', help='This opton is mandatory. Specifies path to the first input file.')
    parser.add_argument('-I2', '--input2', nargs='*', help='This option is mandatory. Specifies path to the second input file.')
    parser.add_argument('-O', '--output', nargs='*',default=[], help='Optional argument.Provides user an option to specify an output filename.')
    parser.add_argument('-S', '--source',action='store' ,nargs='*',default=['all'],help='Provides user a choice to specify sources (example: UniProt, InterPro) separated by spaces. Default is all.')
    parser.add_argument('-P', '--pubmed',default='F',help='Allows user to turn on the pubmed filter. If turned on, GO terms w/o any Pubmed references will not be considered part of the benchmark set.By default, it is turned off.')
    parser.add_argument('-F', '--confidence',default='F',help='Allows user to turn on the annotation confidence filter. If turned on, GO terms assignments to proteins that are documented in few papers (4 or less by default) will not be considered part of the benchmark set.By default, it is turned off.')
    parser.add_argument('-T', '--threshold',type=int, default=4,help='Allows users to specify a threshold for the minimum number of papers tobe used for having a confident annotation. If not specified, defaults to a value of 4.')
    parser.add_argument('-B', '--blacklist', nargs='*',default=[], help='This parameter can take in a list of pubmed ids and all GO terms andproteins annotated in them will be eliminated from the benchmark set.Default is an empty list.')
    parse(parser, ConfigParam=defaultdict())

    
