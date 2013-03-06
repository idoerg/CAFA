#!/usr/bin/python

import os
import sys
import re
from collections import defaultdict

def main():
    infile = sys.argv[1]
    outfile_name = infile.split('_')[0] + '_prediction_with_SP_id.txt'
    
    target_file = open('all_cafa_targets.fasta', 'r')

    cafa_id_map_swiss_id = defaultdict()
    for lines in target_file:
        newlines = re.sub(r'\n','',lines)
        if newlines.startswith('>'):
            swiss_prot_id = newlines.split(' ')[1].replace('(','').replace(')','')
            cafa_id = newlines.split(' ')[0].strip().replace('>','')
            cafa_id_map_swiss_id[cafa_id] = swiss_prot_id

    outfile_handle = open(outfile_name, 'w')

    prediction_file = open(infile, 'r')
    for data in prediction_file:
        if data.startswith('END'):
            continue
        [Id,prediction,threshold] = re.sub(r'\n','',data).split('\t')
        if not cafa_id_map_swiss_id.has_key(Id):
            continue
        if re.match('gi', cafa_id_map_swiss_id[Id]):
            continue
        else:
            print >> outfile_handle, cafa_id_map_swiss_id[Id] + '\t' + prediction + '\t' + threshold
        
    
if __name__ == "__main__":
    main()
