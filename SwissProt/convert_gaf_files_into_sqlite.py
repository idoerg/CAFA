#!/usr/bin/env python

import os
import sys
import create_SP_only_protein_dataset
import sqlite3
import GOAParser # In future, this module will be replaced with the Bio-Python module GOA.py in Bio.UniProt

'''
    This script takes a uniprot-goa gaf format file as input and converts it into a table in a sqlite database.
    A single table, by the name of uniprot-goa, will be created that will hold all values from the gaf file
    
    As of now, the tabe is created according to the existing gaf file formats of 1.0 and 2.0.
    If in future other file formats, with different column names come up, the table columns need to be changed manually in the script

    Usage:
    python convert_gaf_files_into_sqlite.py <gaf format file>

    Output:
    A .db file to be read queried through sqlite

'''

def insert_into_db(conn, rec, GAFFIELDS):

    # This module takes in a tuple to be inserted into the sqlite database

    c = conn.cursor()
    if len(GAFFIELDS) == 17:
        c.executemany("insert into uniprot_goa values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rec)
    elif len(GAFFIELDS) == 15:
        c.executemany("insert into uniprot_goa values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rec)
        
    conn.commit()
    
def gaf_parser(rec, outfile, GAFFIELDS, record):
    t = ()

    if len(GAFFIELDS) == 15:
        t = (rec['DB'], rec['DB_Object_ID'], rec['DB_Object_Symbol'], ('|'.join(rec['Qualifier'])), rec['GO_ID'], ('|'.join(rec['DB:Reference'])), rec['Evidence'], ('|'.join(rec['With'])), rec['Aspect'], ('|'.join(rec['DB_Object_Name'])), ('|'.join(rec['Synonym'])), rec['DB_Object_Type'], ('|'.join(rec['Taxon_ID'])), rec['Date'], rec['Assigned_By'])
    elif len(GAFFIELDS) == 17:
        t = (rec['DB'], rec['DB_Object_ID'], rec['DB_Object_Symbol'], ('|'.join(rec['Qualifier'])), rec['GO_ID'], ('|'.join(rec['DB:Reference'])), rec['Evidence'], ('|'.join(rec['With'])), rec['Aspect'], rec['DB_Object_Name'], ('|'.join(rec['Synonym'])), rec['DB_Object_Type'], ('|'.join(rec['Taxon_ID'])), rec['Date'], rec['Assigned_By'], rec['Annotation_Extension'], rec['Gene_Product_Form_ID'])
    
    record.append(t)
    return record


if __name__ == '__main__':
    gaf_file = sys.argv[1]
    outfile = gaf_file + '.db'
    index = 0
    record = []

    # sqlite3 connection being established
    conn = sqlite3.connect(outfile)                                                                                               
    c = conn.cursor()                                                                                                                        
    c.execute("drop table if exists uniprot_goa")

    
    # Reads in gaf format file using the iterator in GOAParser module
    gaf_handle = open(gaf_file, 'r')
    parser = GOAParser.gafiterator(gaf_handle)

    
    # Creates a table depending on the version of the gaf file
    for rec in parser:
        if len(rec) == 15:
            c.execute("create table uniprot_goa(db varchar(20), db_id varchar(20), db_symbol varchar(20), qualifier varchar(20), GO_Term varchar(40),db_ref varchar(40), evidence varchar(3), With varchar(20), ontology char(1), db_name varchar(100), synonym varchar(200), db_type varchar(40),taxid varchar(20), Date date, source varchar(40))")
            GAFFIELDS = GOAParser.GAF10FIELDS
            break
        elif len(rec) == 17:
            c.execute("create table uniprot_goa(db varchar(20), db_id varchar(20), db_symbol varchar(20), qualifier varchar(20), GO_Term varchar(40),db_ref varchar(40), evidence varchar(3), With varchar(20), ontology char(1), db_name varchar(100), synonym varchar(200), db_type varchar(40),taxid varchar(20), Date date, source varchar(40), ann_ext varchar(20), gene_product varchar(20))")
            GAFFIELDS = GOAParser.GAF20FIELDS
            break


    # Goes through each record, creates a tuple and inserts it into the db.Due to memory limits,
    # 10,000 record tuple is inserted into the db at a time instead of doing all together.
    for rec in parser:
        index +=1
        record = gaf_parser(rec, outfile, GAFFIELDS, record)
        if index == 10000:
            new_record = tuple(record)
            insert_into_db(conn,new_record, GAFFIELDS)
            index = 0
            record = []

    conn.close()
