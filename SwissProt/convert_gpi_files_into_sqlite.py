#!/usr/bin/env python

import os
import sys
import create_SP_only_protein_dataset
import sqlite3
import GOAParser # In future, this module will be replaced with the Bio-Python module GOA.py in Bio.UniProt

'''                                                                                                                                          
    This script takes a uniprot-goa gpi format file as input and converts it 
    into a table in a sqlite database.A single table, by the name of uniprot-goa, 
    will be created that will hold all values from the gpi file                                  
                                                                                                                                             
    As of now, the tabe is created according to the existing gpi file formats of 1.0 and 1.1.                                                
    If in future other file formats, with different column names come up, 
    the table columns need to be changed manually in the script        
                                                                                                                                             
    Usage:                                                                                                                                   
    python convert_gpi_files_into_sqlite.py <gpi format file>                                                                                
                                                                                                                                             
    Output:                                                                                                                                  
    A .db file to be read queried through sqlite                                                                                             
                                                                                                                                             
'''

def insert_into_db(conn, record):

     # This module takes in a tuple to be inserted into the sqlite database
    c = conn.cursor()
    c.executemany("insert into uniprot_goa values(?,?,?,?,?,?,?,?,?)", record)
    conn.commit()

def gpi_parser(rec, outfile, record):

    if rec.has_key('Gene_Product_Properties'):
        t = (rec['DB_Object_ID'], rec['DB_Object_Symbol'], ('|'.join(rec['DB_Object_Name'])), 
             ('|'.join(rec['DB_Object_Synonym'])), rec['DB_Object_Type'], rec['Taxon'], 
             rec['Parent_Object_ID'], ('|'.join(rec['DB_Xref'])), ('|'.join(rec['Gene_Product_Properties'])))
    else:
        t = (rec['DB'], rec['DB_subset'], rec['DB_Object_ID'], rec['DB_Object_Symbol'], 
             rec['DB_Object_Name'], ('|'.join(rec['DB_Object_Synonym'])), rec['DB_Object_Type'], 
             rec['Taxon'], ('|'.join(rec['Annotation_Target_Set'])))

    record.append(t)
    
    return record

if __name__ == '__main__':

    gpi_file = sys.argv[1]
    outfile = gpi_file + '.db'
    index = 0
    record = []

    # sqlite3 connection being established
    conn = sqlite3.connect(outfile)
    c = conn.cursor()
    c.execute("drop table if exists uniprot_goa")

    # Reads in gpi format file using the iterator in GOAParser module
    gpi_handle = open(gpi_file, 'r')
    parser = GOAParser.gpi_iterator(gpi_handle)

    # Creates a table depending on the version of the gpi file
    for rec in parser:
        if rec.has_key('Gene_Product_Properties'):
            c.execute("create table uniprot_goa(db_id varchar(20), db_symbol varchar(100), " + \
                          "db_name varchar(200), db_synonym varchar(100), db_type varchar(40), " + \
                          "taxid varchar(40), parent_id varchar(40), db_xref varchar(40), " + \
                          "gene_product_properties varchar(200))")
        else:
            c.execute("create table uniprot_goa(db varchar(20), db_subset varchar(40), db_id varchar(20), " + \
                          "db_symbol varchar(100), db_name varchar(200), db_synonym varchar(100), " + \
                          "db_type varchar(40), taxid varchar(40), annotation_target_set varchar(40))")
        break

    # Goes through each record, creates a tuple and inserts it into the db.Due to memory limits,                                             
    # 10,000 record tuple is inserted into the db at a time instead of doing all together.
    for rec in parser:
        index+=1
        record = gpi_parser(rec, outfile, record)
        if index == 10000:
            new_record = tuple(record)
            insert_into_db(conn,new_record)
            index = 0
            record = []

    conn.close()
