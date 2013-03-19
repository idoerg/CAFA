#!/usr/bin/env python
import sys
from collections import defaultdict
import re
import os

def parse_tax_file(tax_filename=''):
    tax_id_name_mapping = defaultdict(int)

    tax_file = open(tax_filename,'r')
    for tax_lines in tax_file:
        cols = tax_lines.strip().split('|')
        cols[0] = cols[0].rstrip()
        cols[1] = cols[1].lstrip()
        cols[2] = cols[2].lstrip()
        cols[3] = cols[3].lstrip()
        if cols[3].rstrip() == 'scientific name':
            tax_id_name_mapping[cols[0].rstrip()] = cols[1].rstrip()

    return tax_id_name_mapping


def t2_filter(t2_file, ontos=set([]),eco_list=set([]),taxids=set([]), pubmed='no', blacklist=set([]), ann_freq=defaultdict(lambda:defaultdict(lambda:set())), paper_threshold=0, tax_filename=''):

    t2_handle = open(t2_file, 'r')
    tax_id_name_mapping = parse_tax_file(tax_filename)

    print 'Parsing ' + t2_file

    outfile  = open(t2_file + ".exponly","w")
    for inline in t2_handle:
        if inline.startswith('!'):
            continue
        tax_ok = False
        eco_ok = False
        onto_ok = False
        ann_ok = False
        pap_ok = False
        inrec = inline.strip().split('\t')
    
        eco_term = inrec[6]
        onto = inrec[8]
        taxid = inrec[12].split(':')[1]
        if tax_id_name_mapping.has_key(taxid):
            organism = re.sub(r' ','_',tax_id_name_mapping[taxid])
            
        #paper_id = inrec[5].split(':')[1]
        
        if pubmed == 'no' and inrec[5] == '':
            continue
        
        if (len(ann_freq) == 0) or (len(ann_freq[fields[1]][fields[4]]) >= paper_threshold):
            ann_ok = True
        if not inrec[5] in blacklist:
            pap_ok = True
        if eco_term in eco_list:
            eco_ok = True
        if (not taxids) or (organism in taxids) or (taxid in taxids):
            tax_ok = True
        if (not ontos) or (onto in ontos):
            onto_ok = True
        if tax_ok and eco_ok and onto_ok and ann_ok and pap_ok:
            outfile.write(str(inrec[1]) + '\t' + str(inrec[8]) + '\t' + str(inrec[4]) + '\n')
    outfile.close()
    tax_id_name_mapping.clear()

def t1_filter_pass1(t1_file,ontos, taxids,
                    eco_iea=set([]),eco_exp=set([]), tax_filename=''):

    tax_id_name_mapping = parse_tax_file(tax_filename)

    print 'Parsing ' + t1_file

    t1_handle = open(t1_file, 'r')

    outfile_iea  = open(t1_file + ".iea1","w")
    outfile_exp  = open(t1_file + ".exp1","w")
    for inline in t1_handle:
        if inline.startswith('!'):
            continue
        tax_ok = False
        onto_ok = False
        eco_iea_ok = False
        eco_exp_ok = False
        inrec = inline.strip().split('\t')
        
        eco_term = inrec[6]
        onto = inrec[8]
        taxid = inrec[12].split(':')[1]
        if tax_id_name_mapping.has_key(taxid):
            organism = re.sub(r' ','_',tax_id_name_mapping[taxid])
        
        if eco_term in eco_iea:
            eco_iea_ok = True
        elif eco_term in eco_exp:
            eco_exp_ok = True
        if (not taxids) or (taxid in taxids) or (organism in taxids):
            tax_ok = True
        if (not ontos) or (onto in ontos):
            onto_ok = True
        if tax_ok and onto_ok and eco_iea_ok:
            outfile_iea.write(inline)
        if tax_ok and onto_ok and eco_exp_ok:
            outfile_exp.write(inline)

    outfile_exp.close()
    outfile_iea.close()
    tax_id_name_mapping.clear()

def t1_filter_pass2(t1_exp_file,t1_iea_file):
    exp_pid_dict = defaultdict(lambda:defaultdict())
    
    for inline in t1_exp_file:
        inrec = inline.strip().split('\t')
        
        exp_pid_dict[inrec[1]][inrec[8]] = None

    outfile1  = open(t1_iea_file.name + ".iea2","w")
    
    for inline in t1_iea_file:
        inrec = inline.strip().split('\t')
        if len(inrec) < 15:
            continue
        
        if exp_pid_dict.has_key(inrec[1]):
            if not exp_pid_dict[inrec[1]].has_key(inrec[8]):
                outfile1.write(str(inrec[1]) + '\t' + str(inrec[8]) + '\t' + 'part_excl' + '\n')
        else:
            outfile1.write(str(inrec[1]) + '\t' + str(inrec[8]) + '\t' + 'all_excl' + '\n')
            
    outfile1.close()
    exp_pid_dict.clear()
    

if __name__ == '__main__':
    t2_filter(file(sys.argv[1])) 
#    t1_filter_pass1(file(sys.argv[1]),ontos=set(['P']))
    #t1_filter_pass2(file(sys.argv[1]), file(sys.argv[2]))
