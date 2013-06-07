#!/usr/bin/env python

import os
import sys
import create_SP_only_protein_dataset
import sqlite3
import GOAParser # In future, this module will be replaced with the Bio-Python module GOA.py in Bio.UniProt

'''                                                                                                                                          
    This script takes a uniprot-goa gpa format file as input and converts it 
    into a table in a sqlite database.A single table, by the name of uniprot-goa, 
    will be created that will hold all values from the gpa file                                  
                                                                                                                                             
    As of now, the tabe is created according to the existing gpa file formats of 1.0 and 1.1.                                                
    If in future other file formats, with different column names come up, 
    the table columns need to be changed manually in the script        
                                                                                                                                             
    Usage:                                                                                                                                   
    python convert_gpa_files_into_sqlite.py <gpa format file>                                                                                
                                                                                                                                             
    Output:                                                                                                                                  
    A .db file to be read queried through sqlite                                                                                             
                                                                                                                                             
'''


def insert_into_db(conn, rec):

    # This module takes in a tuple to be inserted into the sqlite database
    c = conn.cursor()
    c.executemany("insert into uniprot_goa values(?,?,?,?,?,?,?,?,?,?,?,?)", rec)
    conn.commit()
    
    
def gpa_parser(rec, outfile, record):
    t = ()

    if rec.has_key('Annotation_Properties'):
        t = (rec['DB'], rec['DB_Object_ID'], ('|'.join(rec['Qualifier'])), rec['GO_ID'], 
             ('|'.join(rec['DB:Reference'])), rec['ECO_Evidence_code'], ('|'.join(rec['With'])), 
             rec['Interacting_taxon_ID'], rec['Date'], rec['Assigned_by'], 
             ('|'.join(rec['Annotation_Extension'])), rec['Annotation_Properties'])

    elif rec.has_key('Spliceform_ID'):
        t = (rec['DB'], rec['DB_Object_ID'], ('|'.join(rec['Qualifier'])), rec['GO_ID'], 
             ('|'.join(rec['DB:Reference'])), rec['Evidence_code'], ('|'.join(rec['With'])), 
             rec['Interacting_taxon_ID'], rec['Date'], rec['Assigned_by'], 
             ('|'.join(rec['Annotation_Extension'])), rec['Spliceform_ID'])
    
    record.append(t)
    return record


if __name__ == '__main__':
    gpa_file = sys.argv[1]
    outfile = gpa_file + '.db'
    index = 0
    record = []

    # sqlite3 connection being established
    conn = sqlite3.connect(outfile)                                                                                               
    c = conn.cursor()                                                                                                                        
    c.execute("drop table if exists uniprot_goa")

    # Reads in gpa format file using the iterator in GOAParser module
    gpa_handle = open(gpa_file, 'r')
    parser = GOAParser.gpa_iterator(gpa_handle)

    for rec in parser:
        if rec.has_key('Annotation_Properties'):
            c.execute("create table uniprot_goa(db varchar(20), db_id varchar(20), " + \
                          "qualifier varchar(20), GO_Term varchar(40),db_ref varchar(40), " + \
                          "evidence varchar(3), With varchar(20), interacting_taxid varchar(20), " + \
                          "Date date, source varchar(40), ann_ext varchar(20), annotation_properties varchar(40))")

        elif rec.has_key('Spliceform_ID'):
            c.execute("create table uniprot_goa(db varchar(20), db_id varchar(20), qualifier varchar(20), " + \
                          "GO_Term varchar(40),db_ref varchar(40), evidence varchar(3), With varchar(20), " + \
                          "interacting_taxid varchar(20), Date date, source varchar(40), ann_ext varchar(20), " + \
                          "spliceform_id varchar(40))")
        break

    for rec in parser:
        index += 1
        record = gpa_parser(rec, outfile, record)
        if index == 10000:
            new_record = tuple(record)
            insert_into_db(conn,new_record)
            index = 0
            record = []

    conn.close()


