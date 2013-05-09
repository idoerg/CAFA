#!/usr/bin/env python

import os
import sys
import GOAParser
from os.path import basename

def parse_tax_file(tax_filename):
    tax_id_name_mapping = {}

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

def gafiterator_extended(handle):
    """ This function should be called to read a                                                                                         
    gene_association.goa_uniprot file. Reads the first record and                                                                        
    returns a gaf 2.0 or a gaf 1.0 iterator as needed                                                                                    
    """

    inline = handle.readline()
    if inline.strip() == '!gaf-version: 2.0':
        sys.stderr.write("gaf 2.0\n")
        return GOAParser._gaf20iterator(handle),GOAParser.GAF20FIELDS
    else:
        sys.stderr.write("gaf 1.0\n")
        return GOAParser._gaf10iterator(handle),GOAParser.GAF10FIELDS
    

def record_has_extended(inupgrec, ann_freq, allowed, tax_name_id_mapping, EEC_default, outfile, GAFFIELDS):
    """                                                                                                                                   
    Accepts a gaf record, and a dictionary of allowed field values. The                                                                  
    format is {'field_name': set([val1, val2])}.                                                                                         
    If any field in the record has an allowed value, the function stops                                                                  
    searching and returns                                                                                                                
    False. Otherwise, returns true.                                                                                                      
    """

    retval=True
    organism = ''

    for field in allowed:
        if inupgrec['Evidence'] not in EEC_default:
            retval=False
            break
        if not inupgrec.has_key(field):
            if field == 'Pubmed':
                # if there are multiple pubmed identifiers per record, we could change the command below to this
                # if allowed[field] == 'T' and '' in inupgrec['DB:Reference']:
                if allowed[field] == 'T' and inupgrec['DB:Reference'] == '':
                    retval=False
                    break
            elif field == 'Confidence':
                db_id = inupgrec['DB_Object_ID']                                                                                             
                go_id = inupgrec['GO_ID']                                                                                                   
                if allowed[field] == 'T' and len(ann_freq[db_id][go_id]) < allowed['Threshold']:                                             
                    retval=False                                                                                                            
                    break
            elif field == 'Blacklist':
                # if there are multiple pubmed identifiers per record, we could change the command below to this
                # if allowed[field] == 'T' and len(inupgrec['DB:Reference'].intersection(allowed[field])) > 0:
                 if inupgrec['DB:Reference'] in allowed[field]:
                     retval=False
                     break
            else:
                continue
            continue

        if len(allowed[field]) == 0:
            continue

        if field == 'Taxon_ID':
            # In case if a record has multiple taxon ids associated with it, loop through each taxon
            # and check if it matches the allowed values or not or check for an intersection between the 2 sets
            # If the intersection set is > 0, we keep the record. Else, we discard it
            if tax_name_id_mapping.has_key(inupgrec[field].split(':')[1]):
                organism = tax_name_id_mapping[inupgrec[field].split(':')[1]]
            if organism in allowed[field] or inupgrec[field].split(':')[1] in allowed[field]:
                retval=True
            else:
                retval=False
                break
        else:
            if inupgrec[field] not in allowed[field]:
                retval=False
                break        
        
    if retval:
        GOAParser.writerec(inupgrec,outfile, GAFFIELDS)

def t1_filter(t1_iter, t2_exp, t1_file, GAFFIELDS, IEA_default=set([]),EXP_default=set([])):

    t2_exp_handle = open(t2_exp, 'r')
    
    exp_pid_dict = {}
    for inline in t2_exp_handle:
        inrec = inline.strip().split('\t')
        exp_pid_dict[inrec[1]] = None

    t2_exp_handle.close()

    print 'Parsing t1 file : ' + basename(t1_file) + ' ............'

    outfile1  = open(t1_file + ".iea1","w")
    outfile2  = open(t1_file + ".exp1","w")

    for rec in t1_iter:
        if exp_pid_dict.has_key(rec['DB_Object_ID']):
            if rec['Evidence'] in IEA_default:
                GOAParser.writerec(rec, outfile1,GAFFIELDS)
            elif rec['Evidence'] in EXP_default:
                GOAParser.writerec(rec, outfile2, GAFFIELDS)

    outfile1.close()
    outfile2.close()
    exp_pid_dict.clear()