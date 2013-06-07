#!/usr/bin/env python

import os
import sys
from collections import defaultdict
import GOAParser
import GOAParser_cafa
import TargetGenerator

'''
    This script helps capture which species has accumulated maximum experimentally validated GO terms within 
    a certain time period.
    The input to the script is 2 uniprot-goa files at 2 different time points.
    The output will be a tab delimited file with 3 columns : first column is the protein ID, second column is 
    ontology and third column is the taxon id

    Usage:
    python capture_species_with_max_annotation.py <gaf file 1> < gaf file 2> <desired name for output file>


'''

infile1 = sys.argv[1]
infile2 = sys.argv[2]
output_filename = sys.argv[3]


infile1_handle = open(infile1, 'r')
infile2_handle = open(infile2, 'r')

iter_handle = GOAParser.gafiterator(infile2_handle)
for ingen in iter_handle:
    if len(ingen) == 17:
        GAFFIELDS = GOAParser.GAF20FIELDS
        break
    else:
        GAFFIELDS = GOAParser.GAF10FIELDS
        break

EEC_default = set(['EXP','IDA','IPI','IMP','IGI','IMP', 'TAS', 'IC'])

allowed_field = {'Evidence' : EEC_default}
outfile = open(infile2 + '.exponly', 'w')

t2_exp = infile2 + '.exponly'

for ingen in iter_handle:
    retval = GOAParser.record_has(ingen, allowed_field)
    if retval:
        GOAParser.writerec(ingen, outfile, GAFFIELDS)

iter_handle = GOAParser.gafiterator(infile1_handle)
for ingen in iter_handle:
    if len(ingen) == 17:
        GAFFIELDS = GOAParser.GAF20FIELDS
        break
    else:
        GAFFIELDS = GOAParser.GAF10FIELDS
        break

GOAParser_cafa.t1_filter(iter_handle, t2_exp, infile1, GAFFIELDS, EEC_default)

targetType = 0
output1 = infile1 + '.iea1'
output2 = infile1 + '.exp1'
#output_filename = './data/species_distribution_between_current_and_108_version_of_uniprot_goa_TAS.txt'

TargetGenerator.create(output1, output2, output_filename, targetType)
