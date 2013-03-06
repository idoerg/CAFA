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
from matplotlib.ticker import MaxNLocator

# FTP session begins
def ftp_download(time_point, mode):
    if mode == 0:
        ftp_dir = 't1_ftp_dir'
    elif mode == 1:
        ftp_dir = 't2_ftp_dir'
    filename = ''
    file_list = []
    download_status = 0
    
    ftp = FTP('ftp.ebi.ac.uk')
    ftp.login()

    if time_point == 'current':
        remote_dir = 'pub/databases/GO/goa/UNIPROT'
    else:
        [month,year] = time_point.split('_')
        month = month.capitalize()
        remote_dir = 'pub/databases/GO/goa/old/UNIPROT'
    
    ftp.cwd(remote_dir)
    ftp.dir('.', file_list.append)

    if len(file_list) < 10:
        for i in file_list:
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            if not os.path.exists('./'+ ftp_dir + '/'):
                os.makedirs('./'+ ftp_dir + '/')
            else:
                shutil.rmtree('./' + ftp_dir + '/')
                os.makedirs('./'+ ftp_dir + '/')
            download_status = 1
            print "Downloading files from uniprot-goa ......."
            filename = terms[-1]
            local_filename = os.path.join('./'+ ftp_dir + '/' + filename)
            outfile = open(local_filename,'wb')
            ftp.retrbinary('RETR '+filename, outfile.write)
            print "Download Complete !!!!"
            outfile.close()
        ftp.quit()
        
    else:
        for i in file_list:
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            if (terms[18] == month) and (terms[21] == year):
                download_status = 1
                if not os.path.exists('./'+ ftp_dir + '/'):
                    os.makedirs('./'+ ftp_dir + '/')
                else:
                    shutil.rmtree('./' + ftp_dir + '/')
                    os.makedirs('./'+ ftp_dir + '/')
                print "Downloading files from uniprot-goa ......."
                filename = terms[-1]
                local_filename = os.path.join('./'+ ftp_dir + '/' + filename)
                outfile = open(local_filename,'wb')
                ftp.retrbinary('RETR '+filename, outfile.write)
                print "Download Complete !!!!"
                outfile.close()
        ftp.quit()
    if download_status == 0:
        print 'There is no file in the time frame specified. Please check and re-run the program'
        sys.exit(1)
    return ftp_dir

# Extract the downloaded files

def extract_downloads(download_dir, mode):
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
    
    return unzipped_file

def plot_distributions(input_dict, benchmark_file):
    file_type = (benchmark_file.split('_')[-1]).split('.')[0]
    pname = 'distribution_of_ontologies_in_' + benchmark_file.split('_')[-3] + '_' + benchmark_file.split('_')[-2] + '_' + file_type
    x_val = []
    y_val = []
    x = range(len(input_dict))
    xTickNames = []
    index = 0

    fig = py.figure()
    py.ylabel('Frequency')
    
    for key1 in input_dict:
        x_val.append(index)
        y_val.append(len(input_dict[key1]))
        if key1 == 'F':
            xTickNames.append('Molecular_Function')
        elif key1 == 'P':
            xTickNames.append('Biological_Process')
        elif key1 == 'C':
            xTickNames.append('Cellular_Component')
        index = index + 1
    py.bar(x_val,y_val,facecolor='red', width=0.25, align='center')
    py.xticks(x, xTickNames)
    
    fig.autofmt_xdate()
    fig.savefig(pname.strip()+'.png')
    
    
# Create plots to view dataset statistics

def calculate_statistics(benchmark_file):

    outfile_name = 'stats_file_for_' + benchmark_file.split('_')[-3] + '_' + benchmark_file.split('_')[-2] + '_' + benchmark_file.split('_')[-1]
    #outfile_name.replace('txt','csv')
    unique_prot = defaultdict(int)
    unique_ann = defaultdict(int)
    dist_ontologies = defaultdict(defaultdict)
    dist_organisms = defaultdict(defaultdict)
    
    outfile = open(outfile_name, 'w')
    file_handle = open(benchmark_file, 'r')
    for lines in file_handle:
        corr_lines = re.sub(r'\n','',lines)
        fields = corr_lines.split('\t')
        if len(fields) < 7:
            continue
        unique_prot[fields[0]] = 1
        unique_ann[fields[1]] = 1
        dist_ontologies[fields[4]][fields[1]] = 1
        dist_organisms[fields[-1]][fields[0]] = 1

    print >> outfile, 'Number Of Unique Proteins in Benchmark set : \t' + str(len(unique_prot))
    print >> outfile, 'Number Of Unique Annotations in Benchmark set : \t' + str(len(unique_ann))
    #print >> outfile, str(len(unique_prot)) + '\t' + str(len(unique_ann))
    print >> outfile, '**************************************'
    print >> outfile, '**************************************'

    print >> outfile, 'Organisms\tFrequency'
    print >> outfile, '**************************************'
    for key1 in dist_organisms:
        print >> outfile, key1 + '\t' + str(len(dist_organisms[key1]))

    plot_distributions(dist_ontologies, benchmark_file)

# The first step with using the argparse module is to create a parser object that can then parse all the user inputs and convert them into python objects based on the user input types provided

print "Welcome to the Benchmark Creation tool !!!!!"
print "*************************************************"

parser = argparse.ArgumentParser(prog='benchmark.py',description='Creates a set of benchmark proteins')
parser.add_argument('-O','--organism',nargs='+', default='all',help='Specifies a set of organisms (multiple organisms to be separated by space) whose proteins will be considered for benchmarking. Default is all organisms')
parser.add_argument('-N','--ontology',nargs='+', default='all',help='Specifies the set of ontologies(multiple ontologies to be separated by space) to be used. By default, all 3 ontologies will be used. Default is all 3 ontologies')
parser.add_argument('-V','--evidence',nargs='+', default='all',help='Specifies the evidence codes to be considered (multiple codes separated by space). By default, all experimentally validated evidence codes (as per GO standards) will be considered. Default is all experimental evidence codes')
parser.add_argument('--cafa',action='store', default=False ,help='Specifies whether a user is a CAFA participant or not (True/False). Default is False')
parser.add_argument('--t1',action='store',help='Specifies the path to a Target file (either CAFA Targets File or any other. If not specified, defaults to None')
parser.add_argument('--t2',action='store' ,help='Specifies either the path to a file with experimental evidence codes or mentions a version in MM_YYYY format (for eg: Dec_2006)to be downloaded.If not specified, defaults to None')
parser.add_argument('-S', '--source',action='store' ,nargs='+',default='all',help='Provides filter options on the datbaases that assigned a particular annotation. If not specified, the program returns results from all sources.')

args = parser.parse_args()

if args.organism :
    user_organism = args.organism
elif args.O:
    user_organism = args.O
else:
    user_organism = 'all'

if args.ontology:
    user_ontology = args.ontology
elif args.N:
    user_ontology = args.N
else:
    user_ontology = 'all'

if args.evidence:
    user_evidence = args.evidence
elif args.V:
    user_evidence = args.V
else:
    user_evidence = 'all'

cafa_user = args.cafa

if args.source:
    source = args.source
elif args.S:
    source = args.S

t1_ftp_dir = ''
t2_ftp_dir = ''
cafa_input_file = ''
t1_input_file = ''
t2_input_file = ''
cafa_handle = ''
t1_handle = ''
t2_handle = ''
outfile_handle = ''

if cafa_user == 'True':
    if not args.t1 == None: 
        cafa_input_file = args.t1
    elif args.t1 == '':
        print "Enter a valid filename"
        sys.exit(1)
    else:
        print "Please enter a valid t1 File"
        sys.exit(1)
else:
    if not args.t1 == None:
        mode = 0
        if re.match('[a-zA-Z]+\_\d+',args.t1):
            t1_ftp_dir = ftp_download(args.t1,mode)
            t1_input_file = extract_downloads(t1_ftp_dir, mode)
            t1_handle = open('./t1_ftp_dir/' + t1_input_file, 'r')
        elif re.match('current', args.t1, re.IGNORECASE):
            t1_ftp_dir = ftp_download(args.t1,mode)
            t1_input_file = extract_downloads(t1_ftp_dir, mode)
            t1_handle = open('./t1_ftp_dir/' + t1_input_file, 'r')
        else:
            t1_input_file = args.t1
            t1_handle = open(t1_input_file, 'r')
    elif args.t1 == '':
        print "Please enter a valid file name"
        sys.exit(1)
    else:
        print "Please enter a valid file name"
        sys.exit(1)

if not args.t2 == None:
    mode = 1
    if re.match('[a-zA-Z]+\_\d+',args.t2):
        t2_ftp_dir = ftp_download(args.t2,mode)
        t2_input_file = extract_downloads(t2_ftp_dir, mode)
        t2_handle = open('./t2_ftp_dir/' + t2_input_file ,'r')
    elif re.match('current', args.t2, re.IGNORECASE):
        t2_ftp_dir = ftp_download(args.t2,mode)
        t2_input_file = extract_downloads(t2_ftp_dir, mode)
        t2_handle = open('./t2_ftp_dir/' + t2_input_file ,'r')
    else:
        t2_input_file = args.t2
        t2_handle = open(t2_input_file ,'r')
elif args.t2 == '' :
    print "Please enter a valid file name"
    sys.exit(1)
else:
    print "Please enter a valid uniprot-goa Experimental File"
    sys.exit(1)

#***********************************************************************************************
# User parameter values
#For Organism

EEC_default = set(['EXP','IDA','IPI','IMP','IGI','IEP'])

if len(user_organism) == 1 and user_organism[0] == '':
    ORG_user = set()
elif (user_organism == 'all') or ('all' in user_organism):
    ORG_user = set()
else:
    ORG_user = set(user_organism)

if len(source) == 1 and source[0] == '':
    source_user = set()
elif (source == 'all') or ('all' in source):
    source_user = set()
else:
    source_user = set(source)

# For Ontology
if len(user_ontology) == 1 and user_ontology[0] == '':
    ONT_user = set(['F','P','C'])
elif (user_ontology == 'all') or ('all' in user_ontology):
    ONT_user = set(['F','P','C'])
else:
    ONT_user = set(user_ontology)

# For Evidence
if len(user_evidence) == 1 and user_evidence[0] == '':
    EEC_user = set(['EXP','IDA','IPI','IMP','IGI','IEP'])
elif (user_evidence == 'all') or ('all' in user_evidence):
    EEC_user = set(['EXP','IDA','IPI','IMP','IGI','IEP'])
else:
    EEC_user = set(user_evidence)

#*********************************************************************************************
#Parsing NCBI taxonomy file
tax_id_name_mapping = defaultdict(int)

tax_file = open('names.dmp','r')
for tax_lines in tax_file:
    new_tax_lines = re.sub(r'\n','',tax_lines)
    cols = new_tax_lines.split('|')
    cols[0] = cols[0].rstrip()
    cols[1] = cols[1].lstrip()
    cols[2] = cols[2].lstrip()
    cols[3] = cols[3].lstrip()
    if cols[3].rstrip() == 'scientific name':
        tax_id_name_mapping[cols[0].rstrip()] = cols[1].rstrip()

#***********************************************************************************************
# Now that the user arguments have been saved into python objects, the next step will be to parse the files according to the user parameters (stored above) and create a benchmark file. The 2 input files are currently of the same format as a uniprot-goa file. 

index = 1
if len(t2_input_file.split('.')) == 3:
    outfile = 'Benchmark_for_' + t2_input_file.split('.')[1] + '_' + t2_input_file.split('.')[2] + '_' + str(index) + '_default.txt'
elif len(t2_input_file.split('.')) == 2:
    outfile = 'Benchmark_for_' + t2_input_file.split('.')[1] + '_' + 'current' + '_' + str(index) + '_default.txt'

while os.path.exists(outfile):
    index = index + 1
    if len(t2_input_file.split('.')) == 3:
        outfile = 'Benchmark_for_' + t2_input_file.split('.')[1] + '_' + t2_input_file.split('.')[2] + '_' + str(index) + '_default.txt'
    elif len(t2_input_file.split('.')) == 2:
        outfile = 'Benchmark_for_' + t2_input_file.split('.')[1] + '_' + 'current' + '_' + str(index) + '_default.txt'

outfile_handle = open(outfile,'w')

if len(t2_input_file.split('.')) == 3:
    version_number = t2_input_file.split('.')[2]
elif len(t2_input_file.split('.')) == 2:
    version_number = 'current'

count = 0

if not cafa_input_file == '':
    protein_dict = defaultdict(int)
    cafa_handle = open(cafa_input_file ,'r')
    for lines in cafa_handle:
        newlines = re.sub(r'\n','',lines)
        if newlines.startswith('>'):
            protein_id = newlines.split(' ')[0]
            protein_dict[protein_id] = 1

elif not t1_input_file == '':
    protein_go_dict = defaultdict(defaultdict)
    
    for lines in t1_handle:
        if lines.startswith('!gaf-version'):
            continue
        newlines = re.sub(r'\n','',lines)
        cols = newlines.split('\t')
    
        if cols[6] == 'IEA':
            protein_go_dict[cols[1]][cols[4]] = 1

black_set = set()
pubmed_option = raw_input('Do you wanna include GO terms that do not have a PubMed reference associated with them : ')

annotation_confidence = raw_input('Do you wanna include annotations that appear in few papers : ')

if annotation_confidence == 'no':
    paper_threshold = raw_input('What is your threshold for the minimum number of papers : ')
    paper_term = defaultdict(lambda:defaultdict(set))
    annotation_conf_index = 1
else:
    annotation_conf_index = 0

if not os.path.exists('papers_with_annotation_frequency_for_' + version_number + '_' + str(index) + '.txt'):
    paper_annotation_freq  = 'papers_with_annotation_frequency_' + version_number + '_' + str(index) + '.txt'
    paper_ann_freq_handle = open(paper_annotation_freq, 'w')
    paper_prot_freq = defaultdict(defaultdict)
    paper_prot_freq_index = 1
    black_set = set()
else:
    paper_prot_freq_index = 0
    blacklist_papers = raw_input('Provide a list of pubmed ids (separated by space if providing multiple ids) to be blacklisted : ')
    if not blacklist_papers == '':
        pubmed_id = blacklist_papers.split(' ')
        black_set = set()
        for i in pubmed_id:
            black_set.add(i)

for line in t2_handle:
    if line.startswith('!gaf-version'):
        continue
    newline = re.sub(r'\n','',line)
    fields = newline.split('\t')
    if len(fields) < 15:
        continue
    taxon_id = fields[12].split(':')[1]
    
    if pubmed_option == 'no' and fields[5] == '':
        continue

    if fields[5] != '':
        paper_id = fields[5].split(':')[1]
    else:
        paper_id = ' '

    if tax_id_name_mapping.has_key(taxon_id):
        organism = re.sub(r' ','_',tax_id_name_mapping[taxon_id])
        
        if (user_organism == 'all')  or ('all' in user_organism) or (user_organism[0] == ''):
            ORG_user.add(organism)
        if (source == 'all') or ('all' in source) or (source[0] == ''):
            source_user.add(fields[-1])

        if not cafa_handle == '':
            if protein_dict.has_key(fields[1]):
                if fields[6] in EEC_user:
                    print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' + fields[6] + '\t' + fields[8] + '\t' + fields[-1] + '\t' + organism
                    count = 1
                    if annotation_conf_index == 1:
                        paper_term[fields[1]][fields[4]].add(str(fields[5]))
                        
                    if paper_prot_freq_index == 1:
                        paper_prot_freq[paper_id][fields[1]] = 1
                #if fields[6] in EEC_user and fields[8] in ONT_user and organism in ORG_user and fields[-1] in source_user:
                 #   count = 1
                  #  print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' +fields[8] + '\t' + fields[-1]

        elif not t1_handle == '':
            if protein_go_dict.has_key(fields[1]):
                if protein_go_dict[fields[1]].has_key(fields[4]):
                    if fields[6] in EEC_user:
                        print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' + fields[6] + '\t' + fields[8] + '\t' + fields[-1] + '\t' + organism
                        count = 1
                        if annotation_conf_index == 1:
                            paper_term[fields[1]][fields[4]].add(str(fields[5]))
                        
                        if paper_prot_freq_index == 1:
                            paper_prot_freq[paper_id][fields[1]] = 1
                        
                        
        else:
            if fields[6] in EEC_user and fields[8] in ONT_user and organism in ORG_user and fields[-1] in source_user:
                count = 1
                print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' + fields[8] + '\t' + fields[-1]


final_op_file = 'Benchmark_for_' + t2_input_file.split('.')[1] + '_' + version_number + '_' + str(index) + '_confident.txt' 
final_op_handle = open(final_op_file, 'w')

if annotation_confidence == 'no':
    ann_conf_handle = open(outfile, 'r')
    for lines in ann_conf_handle:
        newlines = re.sub(r'\n','',lines)
        cols = newlines.split('\t')
        if len(cols) < 7:
            continue
        if paper_term.has_key(cols[0]):
            if paper_term[cols[0]].has_key(cols[1]):
                if cols[4] in ONT_user and cols[-1] in ORG_user and cols[5] in source_user and len(paper_term[cols[0]][cols[1]]) >= int(paper_threshold):
                    if cols[2] not in black_set:
                         print >> final_op_handle, cols[0] + '\t' + cols[1] + '\t' + cols[2] +'\t' + cols[3] + '\t' + cols[4] + '\t' + cols[5] + '\t' + cols[6]

elif annotation_confidence == 'yes':
    ann_conf_handle = open(outfile, 'r')
    for lines in ann_conf_handle:
        newlines = re.sub(r'\n','',lines)
        cols = newlines.split('\t')
        if len(cols) != 7:
            continue
        
        if cols[4] in ONT_user and cols[-1] in ORG_user and cols[5] in source_user:
            if cols[2] not in black_set:
                print >> final_op_handle, cols[0] + '\t' + cols[1] + '\t' + cols[2] +'\t' + cols[3] + '\t' + cols[4] + '\t' + cols[5] + '\t' + cols[6]
                    
calculate_statistics(outfile)
calculate_statistics(final_op_file)

if paper_prot_freq_index == 1:
    for i in paper_prot_freq:
        print >> paper_ann_freq_handle, i + '\t' + str(len(paper_prot_freq[i]))

if count == 1:
    print "Congratulations ! Your benchmark file has been created\n"
else:
    print "Sorry ! The parameters did not match any benchmark protein\n"
    os.remove(outfile)
    os.remove(final_op_file)
