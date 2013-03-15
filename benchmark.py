#!/usr/bin/python

import os
import sys
import numpy as np
import re
from collections import defaultdict
import argparse
from ftplib import FTP
import shutil
from matplotlib import pyplot as py
import argParser
import uniprot_ftp
import filter_ecodes
import parse_bench_proteins
import count_papers_per_annotation
import count_ann_per_paper
import subprocess

# Extract the downloaded files

def extract_downloads(download_dir):
    version_number = []
    index = 0
    unzipped_file = ''

    if not download_dir == '' :
        for root,dirs,files in os.walk('./' + download_dir + '/'):
            if len(files) > 1:
                for filename in files:
                    version_number.append(filename.split('.')[2])
                    version_number.sort()
                    
                    filepath = root + filename.split('.')[0] + '.' + filename.split('.')[1] + '.' + version_number[-1] + '.gz'
                    os.system('gunzip ' + filepath)
                    unzipped_file = os.path.basename(re.sub('.gz','',filepath))
            else:
                filepath = root + files[0]
                os.system('gunzip ' + filepath)
                unzipped_file = os.path.basename(re.sub('.gz','',filepath))
                shutil.move(download_dir + '/' + unzipped_file, '.')
    
    return unzipped_file

# The first step with using the argparse module is to create a parser object that can then parse all the user inputs and convert them into python objects based on the user input types provided

print "Welcome to the Benchmark Creation tool !!!!!"
print "*************************************************"

parser = argparse.ArgumentParser(prog='bm.py',description='Creates a set of benchmark proteins')
parser.add_argument('-O','--organism',nargs='+', default=['all'],help='Specifies a set of organisms (multiple organisms to be separated by space) whose proteins will be considered for benchmarking. Default is all organisms')
parser.add_argument('-N','--ontology',nargs='+', default=['all'],help='Specifies the set of ontologies(multiple ontologies to be separated by space) to be used. By default, all 3 ontologies will be used. Default is all 3 ontologies')
parser.add_argument('-V','--evidence',nargs='+', default=['all'],help='Specifies the evidence codes to be considered (multiple codes separated by space). By default, all experimentally validated evidence codes (as per GO standards) will be considered. Default is all experimental evidence codes')
parser.add_argument('-C','--cafa',action='store', default='False' ,help='Specifies whether a user is a CAFA participant or not (True/False). Default is False')
parser.add_argument('-I1', '--t1',action='store',help='Specifies the path to a Target file (either CAFA Targets File or any other. If not specified, defaults to None')
parser.add_argument('-I2', '--t2',action='store' ,help='Specifies either the path to a file with experimental evidence codes or mentions a version in MM_YYYY format (for eg: Dec_2006)to be downloaded.If not specified, defaults to None')
parser.add_argument('-S', '--source',action='store' ,nargs='+',default=['all'],help='Provides filter options on the datbaases that assigned a particular annotation. If not specified, the program returns results from all sources.')

args = parser.parse_args()

parsed_dict = argParser.parse(args)

if parsed_dict['user_mode'] == 'True':
    cafa = parsed_dict['t1']
    t2 = parsed_dict['t2']
else:
    t1 = parsed_dict['t1']
    t2 = parsed_dict['t2']


if (re.match('[a-zA-Z]+\_\d+',t1)) or (re.match('current', t1, re.IGNORECASE)):
    uniprot_ftp.download(t1)
    t1_input_file = extract_downloads(t1)
    t1_handle = open(t1_input_file, 'r')
else:
    t1_input_file = t1
    t1_handle = open(t1_input_file, 'r')


if (re.match('[a-zA-Z]+\_\d+',t2)) or (re.match('current', t2, re.IGNORECASE)):
    uniprot_ftp.download(t2)
    t2_input_file = extract_downloads(t2)
    t2_handle = open(t2_input_file, 'r')
else:
    t2_input_file = t2
    t2_handle = open(t2_input_file, 'r')


pubmed_option = raw_input('Do you wanna include GO terms that do not have a PubMed reference associated with them : ')
parsed_dict['pubmed'] = pubmed_option

annotation_confidence = raw_input('Do you wanna include annotations that appear in few papers : ')

if annotation_confidence == 'no':
    paper_threshold = raw_input('What is your threshold number of papers for cut off : ')
    paper_term = count_papers_per_annotation.count(t2_input_file, parsed_dict['user_EVI'])
else:
    paper_threshold = 0
    paper_term = defaultdict(lambda:defaultdict(lambda:set()))

black_set = set()

if not os.path.exists(t2_input_file + '_with_annotations_per_paper.txt'):
    paper_annotation_freq  = t2_input_file + '_with_annotations_per_paper.txt'
    paper_ann_freq_handle = open(paper_annotation_freq, 'w')
    paper_prot_freq = count_ann_per_paper.count(t2_input_file, parsed_dict['user_EVI'])
    
    for i in paper_prot_freq:
        print >> paper_ann_freq_handle, i + '\t' + str(len(paper_prot_freq[i]))

    paper_prot_freq.clear()
else:
    blacklist_papers = raw_input('Provide a list of pubmed ids (separated by space if providing multiple ids) to be blacklisted : ')
    if not blacklist_papers == '':
        pubmed_id = blacklist_papers.split(' ')
        for i in pubmed_id:
            black_set.add(i)


# The next step is to parse t1 file into separate ontologies

EEC_default = set(['EXP','IDA','IPI','IMP','IGI','IEP'])

filter_ecodes.t2_filter(t2_input_file, parsed_dict['user_ONT'], EEC_default, parsed_dict['user_ORG'], parsed_dict['pubmed'], black_set, paper_term, paper_threshold)
filter_ecodes.t1_filter_pass1(t1_input_file, parsed_dict['user_ONT'], parsed_dict['user_ORG'], eco_iea=set(['IEA']), eco_exp=EEC_default)
t1_iea_handle = open(t1_input_file + '.iea1' , 'r')
t1_exp_handle = open(t1_input_file + '.exp1' , 'r')
filter_ecodes.t1_filter_pass2(t1_exp_handle, t1_iea_handle)
t1_excl_iea = t1_input_file + '.iea1.iea2'
t2_excl_exp = t2_input_file + '.exponly'
parse_bench_proteins.parse(t2_excl_exp, t1_excl_iea, parsed_dict['user_ONT'])
filename = t2_input_file + '.exponly_benchmark_set.txt'
output_filename = t2_input_file + '_benchmark_set.txt'
subprocess.call(['./remove_duplicates.sh '+ filename + ' ' + output_filename], shell=True)
os.remove(t1_input_file + '.iea1')
os.remove(t1_input_file + '.exp1')
os.remove(t1_input_file + '.iea1.iea2')
os.remove(t2_input_file + '.exponly')
os.remove(filename)
