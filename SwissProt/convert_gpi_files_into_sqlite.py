#!/usr/bin/env python

import os
import sys
import create_SP_only_protein_dataset
import sqlite3
import GOAParser

def insert_into_db(conn, record):
    
    c = conn.cursor()
    c.executemany("insert into uniprot_goa values(?,?,?,?,?,?,?,?,?)", record)
    conn.commit()

def gpi_parser(rec, outfile, GPIFIELDS, index, record):

    t = (rec['DB_Object_ID'], rec['DB_Object_Symbol'], rec['DB_Object_Name'], ('|'.join(rec['DB_Object_Synonym'])), rec['DB_Object_Type'], rec['Taxon'], rec['Parent_Object_ID'], rec['DB_Xrefs'], rec['Gene_Product_Properties'])

    record.append(t)
    
    return record

if __name__ == '__main__':

    gpi_file = sys.argv[1]
    outfile = gpi_file + '.db'
    index = 0
    record = []

    conn = sqlite3.connect(outfile)
    c = conn.cursor()
    c.execute("drop table if exists uniprot_goa")


    gpi_handle = open(gpi_file, 'r')
    inrec = GOAParser.gpi_iterator(gpi_handle)

    for rec in inrec:
        c.execute("create table uniprot_goa(db_id varchar(20), db_symbol varchar(100), db_name varchar(200), db_synonym varchar(100), db_type varchar(40), taxid varchar(40), parent_id varchar(40), db_xref varchar(40), gene_product_properties varchar(200))")
        GPIFIELDS = GOAParser.GPI10FIELDS
        break

    for rec in inrec:
        index = index + 1
        record = gpi_parser(rec, outfile, GPIFIELDS, index, record)
        if index == 3000:
            new_record = tuple(record)
            insert_into_db(conn,new_record)
            index = 0
            record = []

    conn.close()
