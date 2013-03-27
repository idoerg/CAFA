#!/usr/bin/env python

import os
import sys
import re
from collections import defaultdict
import argparse
import shutil
import ArgParser
import CreateDataset
import FilterDataset
import CreateBenchmark
import PaperTermFrequency
import subprocess
import ConfigParser
import Config
import Stats


# The first step with using the argparse module is to create a parser object that can then parse all the user inputs and convert them into python objects based on the user input types provided

print "*************************************************"
print "Welcome to the Benchmark Creation tool !!!!!"
print "*************************************************"

parser = argparse.ArgumentParser(prog='bm.py',description='Creates a set of benchmark proteins')
parser.add_argument('-O','--organism',nargs='*', default=['all'],help='Specifies a set of organisms (multiple organisms to be separated by space) whose proteins will be considered for benchmarking. Default is all organisms')
parser.add_argument('-N','--ontology',nargs='*', default=['all'],help='Specifies the set of ontologies(multiple ontologies to be separated by space) to be used. By default, all 3 ontologies will be used. Default is all 3 ontologies')
parser.add_argument('-V','--evidence',nargs='*', default=['all'],help='Specifies the evidence codes to be considered (multiple codes separated by space). By default, all experimentally validated evidence codes (as per GO standards) will be considered. Default is all experimental evidence codes')
parser.add_argument('-C','--cafa', default='F' ,help='Specifies whether a user is a CAFA participant or not (True/False). Default is False')
parser.add_argument('-I1', '--i1', nargs='*', help='Specifies the path to a Target file (either CAFA Targets File or any other. If not specified, defaults to None')
parser.add_argument('-I2', '--i2', nargs='*', help='Specifies either the path to a file with experimental evidence codes or mentions a version in MM_YYYY format (for eg: Dec_2006)to be downloaded.If not specified, defaults to None')
parser.add_argument('-S', '--source',action='store' ,nargs='*',default=['all'],help='Provides filter options on the datbaases that assigned a particular annotation. If not specified, the program returns results from all sources.')

# Search for config file in the current directory
fname_ind = 0

for root,dirs,files in os.walk('.'):
    for fname in files:
        if fname == '.cafarc':
            fname_ind = 1
            #print 'Config file found.'
            #print '***************************************************************'
    if fname_ind == 0:
        print 'Config file not found'
        print 'Creating new configuration file...'
        print '***************************************************************'
        Config.create()
    break
    
Config = ConfigParser.ConfigParser()
Config.read('.cafarc')
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
               'ftp_file_start' : Config.get('REGEX', 'FTP_FILE_START'),
               'shell_script' : Config.get('SHELL', 'SCRIPT')
               }

work_dir = ConfigParam['workdir']
work_dir = work_dir.rstrip('/')
uniprot_path = ConfigParam['uniprot_path'] .rstrip('/')

if not os.path.exists(work_dir):
    os.makedirs(work_dir)

parsed_dict = ArgParser.parse(parser)

t1 = parsed_dict['t1']
t2 = parsed_dict['t2']

pubmed_option = raw_input('Do you want to consider experimentally validated GO terms without a Pubmed reference to be included in the benchmarking process (y/n) : ')
parsed_dict['pubmed'] = pubmed_option

annotation_confidence = raw_input('Do you want to consider low confidence annotations (these are GO term assignments to proteins that have been recorded in only few papers) (y/n) : ')

if annotation_confidence == 'n':
    paper_threshold = raw_input('What is your threshold number of papers for cut off : ')
    ann_conf_filter = True
else:
    ann_conf_filter = False
    paper_threshold = 0


if parsed_dict['user_mode'] == 'T':
    t1_input_file = work_dir + '/' + CreateDataset.parse_cafa(t1)
else:
    t1_input_file = work_dir + '/' + CreateDataset.parse(t1, ConfigParam)

t2_input_file = work_dir + '/' + CreateDataset.parse(t2, ConfigParam)


black_set = set()

if not os.path.exists(t2_input_file + '_with_annotations_per_paper.txt'):
    paper_annotation_freq  = t2_input_file + '_with_annotations_per_paper.txt'
    paper_conf_filter = True
    paper_ann_freq_handle = open(paper_annotation_freq, 'w')
else:
    paper_conf_filter = False
    blacklist_papers = raw_input('Would you like to eliminate certain pubmed ids from being considered as part of the benchmark process ? If yes, enter a list of pubmed ids separated space. If no, leave blank.')
    if not blacklist_papers == '':
        pubmed_id = blacklist_papers.split(' ')
        for i in pubmed_id:
            black_set.add(i)


if ann_conf_filter or paper_conf_filter : 
    [ann_conf, paper_conf] = PaperTermFrequency.count(t2_input_file, parsed_dict['user_EVI'], ann_conf_filter, paper_conf_filter)

    if len(paper_conf) > 0:
        for i in paper_conf:
            print >> paper_ann_freq_handle, i + '\t' + str(len(paper_conf[i]))

        paper_conf.clear()
else:
    ann_conf = defaultdict(lambda:defaultdict(set))

# The next step is to parse t1 file into separate ontologies

FilterDataset.t2_filter(t2_input_file, parsed_dict['user_ONT'], ConfigParam['exp_eec'], parsed_dict['user_ORG'], parsed_dict['user_source'], parsed_dict['pubmed'], black_set, ann_conf, paper_threshold, ConfigParam['tax_file'])
t2_exp = t2_input_file + '.exponly'

if parsed_dict['user_mode'] == 'T':
    CreateBenchmark.parse_cafa(t2_exp, t1_input_file)
    filename = t2_exp + '_bench.txt'
    index = 1
    while os.path.exists(t2_input_file + '.' + str(index) + '.benchmark'):
        index = index + 1
    output_filename = t2_input_file + '.' + str(index) + '.benchmark'
    
else:
    FilterDataset.t1_filter_pass1(t1_input_file, t2_exp, ConfigParam['iea_eec'], ConfigParam['exp_eec'])
    t1_iea_handle = open(t1_input_file + '.iea1' , 'r')
    t1_exp_handle = open(t1_input_file + '.exp1' , 'r')
    FilterDataset.createT1Excl(t1_exp_handle, t1_iea_handle)
    t1_excl_iea = t1_input_file + '.iea1.iea2'
    t2_excl_exp = t2_input_file + '.exponly'
    CreateBenchmark.parse(t2_excl_exp, t1_excl_iea, parsed_dict['user_ONT'])
    filename = t2_exp + '_bench.txt'

    index = 1
    while os.path.exists(t2_input_file + '.' + str(index) + '.benchmark'):
        index = index + 1
    output_filename = t2_input_file + '.' + str(index) + '.benchmark'
    
subprocess.call([ConfigParam['shell_script'] + ' ' + filename + ' ' + output_filename], shell=True)
Stats.plot_stats(output_filename, uniprot_path)

print 'Cleaning working directory....'

os.remove(filename)
os.remove(t1_input_file + '.iea1')
if (t1_input_file + '.exp1'):
    os.remove(t1_input_file + '.exp1')

if (t1_input_file + '.iea1.iea2'):
    os.remove(t1_input_file + '.iea1.iea2')

os.remove(t2_input_file + '.exponly')

for root, dirs, files in os.walk(work_dir):
    for fname in files:
        if os.path.getsize(root + '/' + fname) == 0:
            os.remove(root + '/' + fname)

print 'Thank you for using the Benchmark Creator Software'
