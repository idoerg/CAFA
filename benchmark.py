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
    ftp_dir = '/home/raji/Desktop/CAFA/ftp_dir/'
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
            if not i.startswith('gene_association'):
                continue
            filename = i
            local_filename = os.path.join(r'/home/raji/Desktop/CAFA/' + filename)
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

# User Input 
test_file = raw_input("Do you have a CAFA Target's File? (yes/no) : ")
if test_file == 'yes':
    t0_pred_set = raw_input("Enter the absolute path to the above file : ")
    t1_file_point = raw_input("Enter the version (in MM_YYYY format) of uniprot-goa from which to consider experimental annotations : ")    
    download_dir = ftp_download(t1_file_point)

# This section is yet to be worked out
elif test_file == 'no':
    download_options = raw_input("Would you like to download the files? (yes/no) : ")
    if download_options == 'yes':
        t0_file_point = raw_input("Enter the time point at which you want to consider non-experimental anntations from uniprot-goa : ")
        print "Downloading target file from UniProt-GOA ........"
        t0_pred_set = 'new_t0_file.txt'
        t1_file_point = raw_input("Enter the time point at which you want to consider experimental anntations from uniprot-goa : ")
        print "Downloading file from uniprot-goa ......."
        t1_pred_set = 'new_t1_file.txt'
    else:
        t0_pred_file = raw_input("Enter absolute path to file containing non-experimental annotations : ")
        t1_pred_file = raw_input("Enter absolute path to file cotaining experimental annotations : ")


# Extract the downloaded files
version_number = []
index = 0
for root,dirs,files in os.walk(download_dir):
    if len(files) > 1:
        for filename in files:
            version_number.append(filename.split('.')[2])
        version_number.sort()
        
        filepath = root + filename.split('.')[0] + '.' + filename.split('.')[1] + '.' + version_number[-1] + '.gz'
        os.system('gunzip ' + filepath)
        t1_pred_set = re.sub('.gz','',filepath)
    else:
        filepath = root + files[0]
        os.system('gunzip ' + filepath)
        t1_pred_set = re.sub('.gz','',filepath)

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

t0_infile = open(t0_pred_set ,'r')
t1_infile = open(t1_pred_set ,'r')

outfile = open('Benchmark_proteins.txt','w')

t0_protein_dict = defaultdict(defaultdict)
count = 0

for lines in t0_infile:
    if lines.startswith('!gaf-version'):
        print 'Parsing a UniProt-GOA file'
        continue
    if not lines.startswith('UniProt'):
        continue
    newlines = re.sub(r'\n','',lines)
    
    terms = newlines.split('\t')
    if terms[6] in EEC_default:
        continue
    t0_protein_dict[terms[1]][terms[4]] = terms[6]

for line in t1_infile:
    if line.startswith('!gaf-version'):
        continue
    if not line.startswith('UniProt'):
        continue
    newline = re.sub(r'\n','',line)
    fields = newline.split('\t')
    #print fields[4] + '\t' +  fields[6] + '\t' + fields[8]
    #db, db_object_id, db_object_symbol, qualifier, go_id, db_reference, evidence, withit, aspect,db_object_name, synonym, db_object_type,taxon_id, date, assigned_by,annotation_extension, gene_product_form_id = newline.split('\t')
    taxon_id = fields[12].split(':')[1]

    if tax_id_name_mapping.has_key(taxon_id):
        organism = re.sub(r' ','_',tax_id_name_mapping[taxon_id])
        
    if t0_protein_dict.has_key(fields[1]):
        if t0_protein_dict[fields[1]].has_key(fields[4]):
            if ORG_user == 1:
                if (fields[6] in EEC_user) and (fields[8] in ONT_user):
                    count = 1
                    print >> outfile, db_object_id + '\t' + go_id + '\t' + aspect
            else:
                if (fields[6] in EEC_user) and (fields[8] in ONT_user) and (organism in ORG_user):
                    count  = 1
                    print >> outfile, fields[2] + '\t' + fields[4] + '\t' + fields[8]

if count == 1:
    print "Congratulations ! Your benchmark file has been created\n"
else:
    print "Sorry ! The parameters did not match any benchmark protein\n"
    os.remove('Benchmark_proteins.txt')
