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

# Create plots to view dataset statistics

#def calculate_statistics(default_op, filtered_op):
    

# The first step with using the argparse module is to create a parser object that can then parse all the user inputs and convert them into python objects based on the user input types provided

print "Welcome to the Benchmark Creation tool !!!!!"
print "*************************************************"

parser = argparse.ArgumentParser(prog='benchmark.py',description='Creates a set of benchmark proteins')
parser.add_argument('-ORG','--Organism',nargs='+', default='all',help='Specifies a set of organisms (multiple organisms to be separated by space) whose proteins will be considered for benchmarking. Default is all organisms')
parser.add_argument('-ONT','--Ontology',nargs='+', default='all',help='Specifies the set of ontologies(multiple ontologies to be separated by space) to be used. By default, all 3 ontologies will be used. Default is all 3 ontologies')
parser.add_argument('-EVI','--Evidence',nargs='+', default='all',help='Specifies the evidence codes to be considered (multiple codes separated by space). By default, all experimentally validated evidence codes (as per GO standards) will be considered. Default is all experimental evidence codes')
parser.add_argument('--CafaMode',action='store', default=False ,help='Specifies whether a user is a CAFA participant or not (True/False). Default is False')
parser.add_argument('--t1',action='store',help='Specifies the path to a Target file (either CAFA Targets File or any other. If not specified, defaults to None')
parser.add_argument('--t2',action='store' ,help='Specifies either the path to a file with experimental evidence codes or mentions a version in MM_YYYY format (for eg: Dec_2006)to be downloaded.If not specified, defaults to None')
parser.add_argument('--sourceDB',action='store' ,nargs='+',default='all',help='Provides filter options on the datbaases that assigned a particular annotation. If not specified, the program returns results from all sources.')

args = parser.parse_args()

if args.Organism:
    user_organism = args.Organism
elif args.ORG:
    user_organism = args.ORG

if args.Ontology:
    user_ontology = args.Ontology
elif args.ONT:
    user_ontology = args.ONT

if args.Evidence:
    user_evidence = args.Evidence
elif args.EVI:
    user_evidence = args.EVI

cafa_user = args.CafaMode
source = args.sourceDB

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
    else:
        print "Please enter a valid t1 File"
        sys.exit(1)
else:
    if not args.t1 == None:
        mode = 0
        if re.match('[a-zA-Z]+\_\d+',args.t1):
            t1_ftp_dir = ftp_download(args.t1,mode)
            t1_input_file = extract_downloads(t1_ftp_dir, mode)
        else:
            t1_input_file = args.t1

if not args.t2 == None:
    mode = 1
    if re.match('[a-zA-Z]+\_\d+',args.t2):
        t2_ftp_dir = ftp_download(args.t2,mode)
        t2_input_file = extract_downloads(t2_ftp_dir, mode)
    else:
        t2_input_file = args.t2
else:
    print "Please enter a valid uniprot-goa Experimental File"
    sys.exit(1)

#***********************************************************************************************
# User parameter values
#For Organism

EEC_default = set(['EXP','IDA','IPI','IMP','IGI','IEP'])

if not (user_organism == 'all') or ('all' in user_organism):
    ORG_user = set(user_organism)

if not (source == 'all') or ('all' in source):
    source_user = set(source)

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

t2_handle = open('./t2_ftp_dir/' + t2_input_file ,'r')

index = 1
outfile = 'Benchmark_for_' + t2_input_file.split('.')[1] + '_' + t2_input_file.split('.')[2] + '_' + str(index) + '_default.txt'

while os.path.exists(outfile):
    index = index + 1
    outfile = 'Benchmark_for_' + t2_input_file.split('.')[1] + '_' + t2_input_file.split('.')[2] + '_' + str(index) + '_default.txt'

outfile_handle = open(outfile,'w')

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
    t1_handle = open('./t1_ftp_dir/' + t1_input_file, 'r')
    for lines in t1_handle:
        if lines.startswith('!gaf-version'):
            continue
        newlines = re.sub(r'\n','',lines)
        cols = newlines.split('\t')
        #if not re.match('UniProt',cols[0]):
         #   continue
        if cols[6] == 'IEA':
            protein_go_dict[cols[1]][cols[4]] = 1

pubmed_option = raw_input('Do you wanna include GO terms that do not have a PubMed reference associated with them : ')

annotation_confidence = raw_input('Do you wanna include annotations that appear in few papers : ')

if annotation_confidence == 'no':
    paper_threshold = raw_input('What is your threshold for the minimum number number of papers : ')
    paper_term = defaultdict(lambda:defaultdict(set))

bias_papers = raw_input('Would you like a list of papers that have annotated too many proteins : ')
if bias_papers == 'yes' :
    bias_threshold = raw_input('Enter the maximum threshold for the number of proteins being annotated in a paper : ')
    paper_prot_freq = defaultdict(defaultdict)
    bias_paper_output = 'list_of_papers_annotating_many_proteins.txt'
    bias_paper_handle = open(bias_paper_output , 'w')

for line in t2_handle:
    if line.startswith('!gaf-version'):
        continue
    newline = re.sub(r'\n','',line)
    fields = newline.split('\t')
    #if not re.match('UniProt',fields[0]):
     #   continue
    taxon_id = fields[12].split(':')[1]
    
    if pubmed_option == 'no' and fields[5] == '':
        continue

    paper_id = fields[5].split(':')[1]


    if tax_id_name_mapping.has_key(taxon_id):
        organism = re.sub(r' ','_',tax_id_name_mapping[taxon_id])
        
        if args.Organism == 'all':
            ORG_user.add(organism)
        if args.sourceDB == 'all':
            source_user.add(fields[-1])

        if not cafa_handle == '':
            if protein_dict.has_key(fields[1]):
                if fields[6] in EEC_user and fields[8] in ONT_user and organism in ORG_user and fields[-1] in source_user:
                    count = 1
                    print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' +fields[8] + '\t' + fields[-1]
                    ORG

        elif not t1_handle == '':
            if protein_go_dict.has_key(fields[1]):
                if protein_go_dict[fields[1]].has_key(fields[4]):
                    if fields[6] in EEC_user:
                        paper_prot_freq[paper_id][fields[1]] = 1
                        paper_term[fields[1]][fields[4]].add(str(fields[5]))
                        print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' + fields[6] + '\t' + fields[8] + '\t' + fields[-1] + '\t' + organism
                        count = 1
                    #if fields[6] in EEC_user and fields[8] in ONT_user and organism in ORG_user and fields[-1] in source_user:
                     #   if annotation_confidence == 'yes':
                      #      count = 1
                       #     print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' + fields[8] + '\t' + fields[-1]
                        #else:
                         #   count = 1
                        
                           # print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' + fields[8] + '\t' + fields[-1]
                    
        else:
            if fields[6] in EEC_user and fields[8] in ONT_user and organism in ORG_user and fields[-1] in source_user:
                count = 1
                print >> outfile_handle, fields[1] + '\t' + fields[4] + '\t' + paper_id + '\t' + fields[8] + '\t' + fields[-1]


final_op_file = 'Benchmark_for_' + t2_input_file.split('.')[1] + '_' + t2_input_file.split('.')[2] + '_' + str(index) + '_with_strong_confidence.txt' 
final_op_handle = open(final_op_file, 'w')

if annotation_confidence == 'no':
    ann_conf_handle = open(outfile, 'r')
    for lines in ann_conf_handle:
        newlines = re.sub(r'\n','',lines)
        cols = newlines.split('\t')
        if paper_term.has_key(cols[0]):
            if paper_term[cols[0]].has_key(cols[1]):
                if cols[4] in ONT_user and cols[-1] in ORG_user and cols[5] in source_user:                  
                    if len(paper_term[cols[0]][cols[1]]) >= int(paper_threshold):
                        print >> final_op_handle, cols[0] + '\t' + cols[1] + '\t' + cols[2] +'\t' + cols[3] + '\t' + cols[4]

#calculate_statistics(outfile, final_op_file)

for i in paper_prot_freq:
    if len(paper_prot_freq[i]) >= int(bias_threshold):
        print >> bias_paper_handle, i

if count == 1:
    print "Congratulations ! Your benchmark file has been created\n"
else:
    print "Sorry ! The parameters did not match any benchmark protein\n"
    os.remove(outfile)
    os.remove(final_op_file)


    
