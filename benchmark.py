#!/usr/bin/python

import os
import sys
import re
from collections import defaultdict
import argparse
from ftplib import FTP
import shutil

# FTP session begins
def ftp_download(time_point, mode):
    if mode == 0:
        ftp_dir = '/home/raji/Desktop/CAFA_new/target_ftp_dir/'
    elif mode == 1:
        ftp_dir = '/home/raji/Desktop/CAFA_new/exp_ftp_dir/'
    filename = ''
    file_list = []
    #ftp_dir = '/home/raji/Desktop/CAFA_new/ftp_dir/'
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
            print "Downloading files from uniprot-goa ......."
            filename = terms[-1]
            local_filename = os.path.join(ftp_dir + filename)
            outfile = open(local_filename,'wb')
            ftp.retrbinary('RETR '+filename, outfile.write)
        outfile.close()
        ftp.quit()
        print "Download Complete !!!!"
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
        print "Download Complete !!!!"
        outfile.close()
        ftp.quit()

    return ftp_dir

# Extract the downloaded files

def extract_downloads(download_dir, mode):
    version_number = []
    index = 0

    unzipped_file = ''

    if not download_dir == '' :
        for root,dirs,files in os.walk(download_dir):
            if len(files) > 1:
                for filename in files:
                    version_number.append(filename.split('.')[2])
                    version_number.sort()
                    
                    filepath = root + filename.split('.')[0] + '.' + filename.split('.')[1] + '.' + version_number[-1] + '.gz'
                    os.system('gunzip ' + filepath)
                    unzipped_file = re.sub('.gz','',filepath)
            else:
                filepath = root + files[0]
                os.system('gunzip ' + filepath)
                unzipped_file = re.sub('.gz','',filepath)
                    
    return unzipped_file

# The first step with using the argparse module is to create a parser object that can then parse all the user inputs and convert them into python objects based on the user input types provided

print "Welcome to the Benchmark Creation tool !!!!!"
print "*************************************************"

parser = argparse.ArgumentParser(prog='benchmark.py',description='Creates a set of benchmark proteins')
parser.add_argument('--organism',nargs='+', default='all',help='Specifies a set of organisms (multiple organisms to be separated by space) whose proteins will be considered for benchmarking. Default is all organisms')
parser.add_argument('--ontology',nargs='+', default='all',help='Specifies the set of ontologies(multiple ontologies to be separated by space) to be used. By default, all 3 ontologies will be used. Default is all 3 ontologies')
parser.add_argument('--evidence',nargs='+', default='all',help='Specifies the evidence codes to be considered (multiple codes separated by space). By default, all experimentally validated evidence codes (as per GO standards) will be considered. Default is all experimental evidence codes')
parser.add_argument('--CAFA_Mode',action='store', default=False ,help='Specifies whether a user is a CAFA participant or not (True/False). Default is False')
parser.add_argument('--Target_File',action='store',help='Specifies an absolute path to a Target file (either CAFA Targets File or any other. If not specified, defaults to None')
parser.add_argument('--Exp_File',action='store' ,help='Specifies either an absolute path to a file with experimental evidence codes or mentions a version in MM_YYYY format (for eg: Dec_2006)to be downloaded.If not specified, defaults to None')

args = parser.parse_args()

user_organism = args.organism
user_ontology = args.ontology
user_evidence = args.evidence
cafa_user = args.CAFA_Mode
target_dir = ''
exp_dir = ''
cafa_target_file = ''
other_target_file = ''
exp_file = ''
cafa_target_infile = ''
other_target_infile = ''
exp_infile = ''

if cafa_user == 'True':
    if not args.Target_File == None: 
        cafa_target_file = args.Target_File
    else:
        print "Please enter a valid Target File"
        sys.exit(1)
else:
    target_file = args.Target_File
    if not target_file == None:
        mode = 0
        if re.match('[a-zA-Z]+\_\d+',target_file):
            target_dir = ftp_download(target_file,mode)
            other_target_file = extract_downloads(target_dir, mode)
        else:
            other_target_file = target_file
    #else:
        #print "Please enter a valid target file"
        #sys.exit(1)

if not args.Exp_File == None:
    mode = 1
    exp_ann_file = args.Exp_File
    if re.match('[a-zA-Z]+\_\d+',exp_ann_file):
        exp_dir = ftp_download(exp_ann_file,mode)
        exp_file = extract_downloads(exp_dir, mode)
    else:
        exp_file = exp_ann_file
else:
    print "Please enter a valid uniprot-goa Experimental File"
    sys.exit(1)

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

if not cafa_target_file == '':
    protein_dict = defaultdict(int)
    cafa_target_infile = open(cafa_target_file ,'r')
    for lines in cafa_target_infile:
        newlines = re.sub(r'\n','',lines)
        if newlines.startswith('>'):
            protein_id = newlines.split(' ')[0]
            protein_dict[protein_id] = 1
elif not other_target_file == '':
    protein_go_dict = defaultdict(defaultdict)
    other_target_infile = open(other_target_file, 'r')
    for lines in other_target_infile:
        newlines = re.sub(r'\n','',lines)
        cols = newlines.split('\t')
        if cols[6] == 'IEA':
            protein_go_dict[cols[1]][cols[4]] = 1

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

        if not cafa_target_infile == '':
            if protein_dict.has_key(fields[1]):
                if ORG_user == 1:
                    if (fields[6] in EEC_user) and (fields[8] in ONT_user):
                        count = 1
                        print >> outfile, fields[2] + '\t' + fields[4] + '\t' + fields[8]
                else:
                    if (fields[6] in EEC_user) and (fields[8] in ONT_user) and (organism in ORG_user):
                        count  = 1
                        print >> outfile, fields[2] + '\t' + fields[4] + '\t' + fields[8]

        elif not other_target_infile == '':
            if protein_go_dict.has_key(fields[1]):
                if protein_go_dict[fields[1]].has_key(fields[4]):
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
