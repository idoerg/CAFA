#!/usr/bin/python

import os
import sys
import re

def create():

    outfile_handle = open('.cafarc', 'w')
    outfile_handle.write('[WORKDIR]\n')
    
    work_dir_response = raw_input('Provide a path to your working directory (If left blank, defaults  to current directory) : ')
    if work_dir_response == '':
        outfile_handle.write('DEFAULT_PATH : .\n') 
    elif work_dir_response.startswith('.') or work_dir_response.startswith('/'):
        outfile_handle.write('DEFAULT_PATH : ' + work_dir_response + '\n')
    else:
        outfile_handle.write('DEFAULT_PATH : ' + './' + work_dir_response + '\n')
        
    outfile_handle.write('\n')

    outfile_handle.write('[FTP]\n')
    outfile_handle.write('HOSTNAME : ftp.ebi.ac.uk\n')
    outfile_handle.write('CURRENT_FILE_PATH : /pub/databases/GO/goa/UNIPROT\n')
    outfile_handle.write('OLD_FILE_PATH : /pub/databases/GO/goa/old/UNIPROT\n')
    outfile_handle.write('\n')
    
    outfile_handle.write('[DEFAULTS]\n')
    outfile_handle.write('EXP_EVIDENCE_CODES : ' + str(set(['EXP','IDA','IPI','IMP','IGI','IEP'])) + '\n')
    outfile_handle.write('IEA_EVIDENCE_CODES : ' + str(set(['IEA'])) + '\n')
    outfile_handle.write('ONTOLOGIES : ' + str(set(['F','P','C'])) + '\n')
    outfile_handle.write('TAXONOMY_FILENAME : names.dmp\n')
    
    outfile_handle.write('\n')

    outfile_handle.write('[SEQUENCE]\n')
    outfile_handle.write('BASE_URL : www.uniprot.org/uniprot/\n')

    outfile_handle.write('\n')

    outfile_handle.write('[REGEX]\n')
    outfile_handle.write('FTP_DATE : [a-zA-Z]+\_\d+\n')
    outfile_handle.write('FTP_FILE_START : gene_association\n')

if __name__ == '__main__':
    create()
