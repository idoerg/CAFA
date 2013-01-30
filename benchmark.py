#!/usr/bin/python

import os
import sys
import re
from collections import defaultdict
import argparse
from ftplib import FTP
import shutil

# FTP session begins
def ftp_download(time_point):
    filename = ''
    file_list = []
    ftp_dir = '/home/raji/Desktop/CAFA_new/ftp_dir/'
    ftp = FTP('ftp.ebi.ac.uk')
    ftp.login()

    if time_point == 'current':
        remote_dir = 'pub/databases/GO/goa/UNIPROT'
    else:
        [month,year] = time_point.split('_')
        remote_dir = 'pub/databases/GO/goa/old/UNIPROT'
    
    ftp.cwd(remote_dir)
    ftp.dir('.', file_list.append)

    if len(file_list) < 10:
        for i in file_list:
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            if not os.path.exists(ftp_dir):
                os.makedirs(ftp_dir)
            filename = terms[-1]
            local_filename = os.path.join(ftp_dir + filename)
            outfile = open(local_filename,'wb')
            ftp.retrbinary('RETR '+filename, outfile.write)
        outfile.close()
        ftp.quit()
        print "Downloaded files from uniprot-goa ......."
    else:
        for i in file_list:
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            if (terms[18] == month) and (terms[21] == year):
                if not os.path.exists(ftp_dir):
                    os.makedirs(ftp_dir)
                print "Downloading files from uniprot-goa ......."
                filename = terms[-1]
                local_filename = os.path.join(ftp_dir + filename)
                outfile = open(local_filename,'wb')
                ftp.retrbinary('RETR '+filename, outfile.write)
        outfile.close()
        ftp.quit()

    return ftp_dir

# The first step with using the argparse module is to create a parser object that can then parse all the user inputs and convert them into python objects based on the user input types provided

print "Welcome to the Benchmark Creation tool !!!!!"
print "*************************************************"

parser = argparse.ArgumentParser(prog='benchmark.py',description='Creates a set of benchmark proteins')
parser.add_argument('--organism',nargs='+', default='all',help='Specifies a set of organisms whose proteins will be considered for benchmarking')
parser.add_argument('--ontology',nargs='+', default='all',help='Specifies the set of ontologies to be used. By default, all 3 ontologies will be used')
parser.add_argument('--evidence',nargs='+', default='all',help='Specifies the evidence codes to be considered. By default, all experimentally validated evidence codes (as per GO standards) will be considered')

args = parser.parse_args()

user_organism = args.organism
user_ontology = args.ontology
user_evidence = args.evidence
target_infile = ''
exp_infile = ''
cafa_target_file = ''
other_target_file = ''
exp_ann_file = ''
download_dir = ''

# User Input 
cafa_file = raw_input("Do you have a CAFA Target File? (yes/no) : ")
if cafa_file == 'yes':
    cafa_target_file = raw_input("Enter the absolute path to the CAFA Target File : ")
    exp_ann_file = raw_input("Enter the version (in MM_YYYY format) of uniprot-goa from which to consider experimental annotations OR Enter path to uniprot-goa file if already downloaded : ")
    if re.match('[a-zA-Z]+\_\d+',exp_ann_file):
        download_dir = ftp_download(exp_ann_file)
    else:
        exp_file = exp_ann_file

else:
    other_file = raw_input("Do you have any target file that you want to use? (yes/no) : ")
    if other_file == 'yes':
        other_target_file = raw_input("Enter the absolute path to Target File : ")
        exp_ann_file = raw_input("Enter the version (in MM_YYYY format) of uniprot-goa from which to consider experimental annotations OR OR Enter path to uniprot-goa file if already downloaded: ")
        if re.match('[a-zA-Z]+\_\d+',exp_ann_file):
            download_dir = ftp_download(exp_ann_file)
        else:
            exp_file = exp_ann_file
    else:
        file_options = raw_input("Would you like to download files from uniprot-goa for creating your benchmark? (yes/no) : ")
        if file_options == 'yes':
            uniprot_version = raw_input("Enter the uniprot-goa version (in MM_YYYY format) to download : ")
            download_dir = ftp_download(uniprot_version)


# Extract the downloaded files
version_number = []
index = 0

if not download_dir == '' :
    for root,dirs,files in os.walk(download_dir):
        if len(files) > 1:
            for filename in files:
                version_number.append(filename.split('.')[2])
                version_number.sort()
                
            filepath = root + filename.split('.')[0] + '.' + filename.split('.')[1] + '.' + version_number[-1] + '.gz'
            os.system('gunzip ' + filepath)
            exp_file = re.sub('.gz','',filepath)
        else:
            filepath = root + files[0]
            os.system('gunzip ' + filepath)
            exp_file = re.sub('.gz','',filepath)

#***********************************************************************************************
# User parameter values
#For Organism

EEC_default = set(['EXP','IDA','IPI','IMP','IGI','IEP'])

if (user_organism == 'all') or ('all' in user_organism):
    ORG_user = 1
else:
    ORG_user = set(user_organism)

# For Ontology
if (user_ontology == 'all') or ('all' in user_ontology):
    ONT_user = set(['F','P','C'])
else:
    ONT_user = set(user_ontology)

# For Evidence
if (user_evidence == 'all') or ('all' in user_evidence):
    EEC_user = set(['EXP','IDA','IPI','IMP','IGI','IEP'])
else:
    EEC_user = set(user_evidence)

#*********************************************************************************************
#Parsing NCBI taxonomy file
tax_id_name_mapping = defaultdict(int)

tax_file = open('/home/raji/Downloads/names.dmp','r')
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

exp_infile = open(exp_file ,'r')

outfile = open('Benchmark_proteins.txt','w')

count = 0

protein_dict = defaultdict(int)

if not cafa_target_file == '':
    target_infile = open(cafa_target_file ,'r')
    for lines in target_infile:
        newlines = re.sub(r'\n','',lines)
        if newlines.startswith('>'):
            protein_id = newlines.split(' ')[0]
            protein_dict[protein_id] = 1
elif not other_target_file == '':
    target_infile = open(other_target_file, 'r')
    for lines in target_infile:
        newlines = re.sub(r'\n','',lines)
        cols = newlines.split('\t')
        protein_dict[cols[0]] = 1

for line in exp_infile:
    if line.startswith('!gaf-version'):
        continue
    if not line.startswith('UniProt'):
        continue
    newline = re.sub(r'\n','',line)
    fields = newline.split('\t')
    taxon_id = fields[12].split(':')[1]

    if tax_id_name_mapping.has_key(taxon_id):
        organism = re.sub(r' ','_',tax_id_name_mapping[taxon_id])

        if not target_infile == '':
            if protein_dict.has_key(fields[1]):
                if ORG_user == 1:
                    if (fields[6] in EEC_user) and (fields[8] in ONT_user):
                        count = 1
                        print >> outfile, fields[2] + '\t' + fields[4] + '\t' + fields[8]
                else:
                    if (fields[6] in EEC_user) and (fields[8] in ONT_user) and (organism in ORG_user):
                        count  = 1
                        print >> outfile, fields[2] + '\t' + fields[4] + '\t' + fields[8]
        else:
            if ORG_user == 1:
                if (fields[6] in EEC_user) and (fields[8] in ONT_user):
                    count = 1
                    print >> outfile, fields[2] + '\t' + fields[4] + '\t' + fields[8]
            else:
                if (fields[6] in EEC_user) and (fields[8] in ONT_user) and (organism in ORG_user):
                    count  = 1
                    print >> outfile, fields[2] + '\t' + fields[4] + '\t' + fields[8]

if count == 1:
    print "Congratulations ! Your benchmark file has been created\n"
else:
    print "Sorry ! The parameters did not match any benchmark protein\n"
    os.remove('Benchmark_proteins.txt')
