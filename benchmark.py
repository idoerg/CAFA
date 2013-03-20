#!/usr/bin/python

import os
import sys
import re
from collections import defaultdict
import argparse
import shutil
import argParser
import CreateDataset
import filter_ecodes
import parse_bench_proteins
import count_ann_per_paper
import subprocess
import ConfigParser
import Stats

Config = ConfigParser.ConfigParser()
Config.read('config.rc')
ConfigParam = defaultdict()

ConfigParam = {'workdir' : Config.get('WORKDIR', 'DEFAULT_PATH'),
               'ftp_host' : Config.get('FTP', 'HOSTNAME'),
               'ftp_curr_path' : Config.get('FTP', 'CURRENT_FILE_PATH'),
               'ftp_old_path' : Config.get('FTP', 'OLD_FILE_PATH'),
               'exp_eec' : Config.get('DEFAULTS', 'EXP_EVIDENCE_CODES'),
               'iea_eec' : Config.get('DEFAULTS', 'IEA_EVIDENCE_CODES'),
               'ont_def' : Config.get('DEFAULTS', 'ONTOLOGIES'),
               'tax_file' : Config.get('DEFAULTS', 'TAXONOMY_FILENAME'),
               'uniprot_path' : Config.get('SEQUENCE', 'BASE_URL'),
               'ftp_date' : Config.get('REGEX', 'FTP_DATE'),
               'ftp_file_start' : Config.get('REGEX', 'FTP_FILE_START')
               }


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

work_dir = ConfigParam['workdir']
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

parsed_dict = argParser.parse(args)

if parsed_dict['user_mode'] == 'True':
    cafa = parsed_dict['t1']
    t2 = parsed_dict['t2']
else:
    t1 = parsed_dict['t1']
    t2 = parsed_dict['t2']

t1_input_file = work_dir + '/' + CreateDataset.parse(t1, ConfigParam)
print t1_input_file
t1_handle = open(t1_input_file, 'r')

t2_input_file = work_dir + '/' + CreateDataset.parse(t2, ConfigParam)
t2_handle = open(t2_input_file, 'r')

pubmed_option = raw_input('Do you wanna include GO terms that do not have a PubMed reference associated with them : ')
parsed_dict['pubmed'] = pubmed_option

annotation_confidence = raw_input('Do you wanna include annotations that appear in few papers : ')

if annotation_confidence == 'no':
    paper_threshold = raw_input('What is your threshold number of papers for cut off : ')
    ann_conf_filter = 1
else:
    ann_conf_filter = 0
    paper_threshold = 0

black_set = set()

if not os.path.exists(t2_input_file + '_with_annotations_per_paper.txt'):
    paper_annotation_freq  = t2_input_file + '_with_annotations_per_paper.txt'
    paper_conf_filter = 1
    paper_ann_freq_handle = open(paper_annotation_freq, 'w')
else:
    paper_conf_filter = 0
    blacklist_papers = raw_input('Provide a list of pubmed ids (separated by space if providing multiple ids) to be blacklisted : ')
    if not blacklist_papers == '':
        pubmed_id = blacklist_papers.split(' ')
        for i in pubmed_id:
            black_set.add(i)

if ann_conf_filter > 0 or paper_conf_filter > 0: 
    [ann_conf, paper_conf] = count_ann_per_paper.count(t2_input_file, parsed_dict['user_EVI'], ann_conf_filter, paper_conf_filter)
    if len(paper_conf) > 0:
        for i in paper_conf:
            print >> paper_ann_freq_handle, i + '\t' + str(len(paper_conf[i]))

        paper_conf.clear()
else:
    ann_conf = defaultdict(lambda:defaultdict(set))

# The next step is to parse t1 file into separate ontologies

filter_ecodes.t2_filter(t2_input_file, parsed_dict['user_ONT'], ConfigParam['exp_eec'], parsed_dict['user_ORG'], parsed_dict['pubmed'], black_set, ann_conf, paper_threshold, ConfigParam['tax_file'])
filter_ecodes.t1_filter_pass1(t1_input_file, parsed_dict['user_ONT'], parsed_dict['user_ORG'], ConfigParam['iea_eec'], ConfigParam['exp_eec'], ConfigParam['tax_file'])
t1_iea_handle = open(t1_input_file + '.iea1' , 'r')
t1_exp_handle = open(t1_input_file + '.exp1' , 'r')
filter_ecodes.t1_filter_pass2(t1_exp_handle, t1_iea_handle)
t1_excl_iea = t1_input_file + '.iea1.iea2'
t2_excl_exp = t2_input_file + '.exponly'
parse_bench_proteins.parse(t2_excl_exp, t1_excl_iea, parsed_dict['user_ONT'])
filename = t2_input_file + '.exponly_bench.txt'
output_filename = t2_input_file + '_benchmark_set.txt'
subprocess.call(['./remove_duplicates.sh '+ filename + ' ' + output_filename], shell=True)
Stats.plot_stats(output_filename, ConfigParam['uniprot_path'])
os.remove(t1_input_file + '.iea1')
os.remove(t1_input_file + '.exp1')
os.remove(t1_input_file + '.iea1.iea2')
os.remove(t2_input_file + '.exponly')
os.remove(filename)
