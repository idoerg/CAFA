#!/usr/bin/env python

import os
import sys
from collections import defaultdict
import sqlite3
import GOAParser

'''
           This script extracts all swiss prot proteins , for a particular taxon, 
           along with its associated information from uniprot-goa files.It takes 
           as input a gene-association file, gene protein information file and a 
           taxon id as input. The first 2 files ideally should be of the same 
           version to avoid missing any proteins and they can be downloaded from 
           uniprot-goa ftp site ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/. 

           Usage :
           python create_SP_only_protein_dataset.py <gene association file> 
                                      <gene protein information file> <taxon id>

           Output:
           .gaf file contains all information in gaf format and 
           .db file that puts all information into a sqlite3 database table

'''

def parse_gpi(infile, taxon=''):

    '''
       This method parses a uniprot-goa gpi file, extracts all proteins
       associated with Swiss-Prot and belonging to the user specified
       taxon and returns them
    '''
    sp_id = defaultdict()

    infile_handle = open(infile, 'r')
    print 'Extracing Swiss Prot ids for the taxa specified'

    parser = GOAParser.gpi_iterator(infile_handle)

    for rec in parser:
        if not rec.has_key('Gene_Product_Properties'):
            print "This version of the gp information file does not contain all required information"
            sys.exit(1)
        else:
            break

    for rec in parser:
        taxid = rec['Taxon'].split(':')[1].strip()
        db = rec['Gene_Product_Properties'][0].split('=')[1].strip()
        if db.startswith('Swiss-Prot') and taxon == taxid:
            sp_id[rec['DB_Object_ID']] = 1

    return sp_id


def extract_gaf(inrec, GAFFIELDS, sp_id, taxon, targetType):

    '''
       Iterates over a gaf record iterator object, filters
       them according to evidence code and returns target proteins
       based on the target type provided.
    '''
    target_prots = defaultdict(lambda:defaultdict())
    target_prots_iea = defaultdict(lambda:defaultdict())
    target_prots_exp = defaultdict(lambda:defaultdict())
    targets_F = {}
    targets_P = {}
    targets_C = {}
    EEC_default = set(['EXP','IDA','IPI','IMP','IGI','IEP'])

    for rec in inrec:
        if sp_id.has_key(rec['DB_Object_ID']):
            protein_ont = rec['Aspect']
            protein_evi = rec['Evidence']
            if protein_evi in EEC_default:
                target_prots_exp[rec['DB_Object_ID']][protein_ont] = 1
            else:
                target_prots_iea[rec['DB_Object_ID']][protein_ont] = 1

    print 'Target generation in progress....'
                
    if targetType == '0':
        for prots in target_prots_iea:
            for ont in target_prots_iea[prots]:
                if target_prots_exp.has_key(prots):
                    if target_prots_exp[prots].has_key(ont):
                        continue
                    target_prots[ont][prots] = 1
                else:
                    target_prots[ont][prots] = 1
                    
    elif targetType == '1':
        for prots in target_prots_exp:
            for ont in target_prots_exp[prots]:
                if target_prots_iea.has_key(prots):
                    if target_prots_iea[prots].has_key(ont):
                        target_prots[ont][prots] = 1

    for ont in target_prots:
        for prots in target_prots[ont]:
            if ont == 'F':
                targets_F[prots] = 1
            elif ont == 'P':
                targets_P[prots] = 1
            elif ont == 'C':
                targets_C[prots] = 1
        

    target_prots.clear()
    target_prots_iea.clear()
    target_prots_exp.clear()
            
    return targets_F, targets_P, targets_C


if __name__ == '__main__':

    gaf_file = sys.argv[1]
    gpi_file = sys.argv[2]
    taxon = sys.argv[3]
    targetType = sys.argv[4]

    gaf_handle = open(gaf_file, 'r')

    sp_id = parse_gpi(gpi_file, taxon)
    inrec = GOAParser.gafiterator(gaf_handle)
    for rec in inrec:
        if len(rec) == 15:
            GAFFIELDS = GOAParser.GAF10FIELDS
            break
        elif len(rec) == 17:
            GAFFIELDS = GOAParser.GAF20FIELDS
            break

    record = extract_gaf(inrec, GAFFIELDS, sp_id, taxon, targetType)
