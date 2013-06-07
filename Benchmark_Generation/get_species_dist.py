#!/usr/bin/env python

import os
import sys
from collections import defaultdict

'''
   This script takes in a tab delimited file containing information as to which proteins
   could be potential benchmark candidates and the species to which they belong to, and creates
   a distribution kind of format as to which species received how many annotations in a particular ontology.

   Usage:
   python get_species_dist.py <tab delimited file> <desired name of output file>

   Output:
   A tab delimited file with 3 columns: Taxon ID, Ontology and number of proteins that gained exp
   evidence over the period of time
'''



infile = sys.argv[1]
outfile = open(sys.argv[2], 'w')

#infile = 'data/species_distribution_between_current_and_108_version_of_uniprot_goa_TAS.txt'
dist = defaultdict(lambda:defaultdict(lambda:set()))
#outfile = open('species_distribution_per_ontology_between_current_and_last_year_with_TAS.txt', 'w')

infile_handle = open(infile, 'r')

for lines in infile_handle:
    fields = lines.strip('\n').split('\t')
    dist[fields[2]][fields[1]].add(fields[0])


for species in dist:
    for ont in dist[species]:
        print >> outfile, species + '\t' + ont + '\t' + str(len(dist[species][ont]))
