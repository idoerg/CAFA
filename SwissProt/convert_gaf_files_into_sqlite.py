#!/usr/bin/env python

import os
import sys
import create_SP_only_protein_dataset
import sqlite3
import GOAParser

def insert_into_db(conn, rec, GAFFIELDS):

    c = conn.cursor()
    if len(GAFFIELDS) == 17:
        c.executemany("insert into uniprot_goa values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rec)
        conn.commit()
    elif len(GAFFIELDS) == 15:
        c.executemany("insert into uniprot_goa values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rec)
        conn.commit()
    
    
def gaf_parser(rec, outfile, GAFFIELDS, index, record):
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

    conn = sqlite3.connect(outfile)                                                                                               
    c = conn.cursor()                                                                                                                        
    c.execute("drop table if exists uniprot_goa")


    gaf_handle = open(gaf_file, 'r')
    inrec = GOAParser.gafiterator(gaf_handle)

    for rec in inrec:
        if len(rec) == 15:
            c.execute("create table uniprot_goa(db varchar(20), db_id varchar(20), db_symbol varchar(20), qualifier varchar(20), GO_Term varchar(40),db_ref varchar(40), evidence varchar(3), With varchar(20), ontology char(1), db_name varchar(100), synonym varchar(200), db_type varchar(40),taxid varchar(20), Date date, source varchar(40))")
            GAFFIELDS = GOAParser.GAF10FIELDS
            break
        elif len(rec) == 17:
            c.execute("create table uniprot_goa(db varchar(20), db_id varchar(20), db_symbol varchar(20), qualifier varchar(20), GO_Term varchar(40),db_ref varchar(40), evidence varchar(3), With varchar(20), ontology char(1), db_name varchar(100), synonym varchar(200), db_type varchar(40),taxid varchar(20), Date date, source varchar(40), ann_ext varchar(20), gene_product varchar(20))")
            GAFFIELDS = GOAParser.GAF20FIELDS
            break

    for rec in inrec:
        index = index + 1
        record = gaf_parser(rec, outfile, GAFFIELDS, index, record)
        if index == 5000:
            new_record = tuple(record)
            insert_into_db(conn,new_record, GAFFIELDS)
            index = 0
            record = []

    conn.close()


