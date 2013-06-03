#!/usr/bin/env python

import os
import sys
import create_SP_only_protein_dataset
import sqlite3
import GOAParser

def insert_into_db(conn, rec):

    c = conn.cursor()
    c.executemany("insert into uniprot_goa values(?,?,?,?,?,?,?,?,?,?,?,?)", rec)
    conn.commit()
    
    
def gpa_parser(rec, outfile, index, record):
    t = ()

    t = (rec['DB'], rec['DB_Object_ID'], ('|'.join(rec['Qualifier'])), rec['GO_ID'], ('|'.join(rec['DB:Reference'])), rec['ECO_Evidence_code'], ('|'.join(rec['With'])), ('|'.join(rec['Interacting_taxon_ID'])), rec['Date'], rec['Assigned_by'], rec['Annotation_Extension'], rec['Spliceform_ID'])
    
    record.append(t)
    return record


if __name__ == '__main__':
    gpa_file = sys.argv[1]
    outfile = gpa_file + '.db'
    index = 0
    record = []

    conn = sqlite3.connect(outfile)                                                                                               
    c = conn.cursor()                                                                                                                        
    c.execute("drop table if exists uniprot_goa")

    gpa_handle = open(gpa_file, 'r')
    inrec = GOAParser.gpa_iterator(gpa_handle)

    for rec in inrec:
        c.execute("create table uniprot_goa(db varchar(20), db_id varchar(20), qualifier varchar(20), GO_Term varchar(40),db_ref varchar(40), evidence varchar(3), With varchar(20), interacting_taxid varchar(20), Date date, source varchar(40), ann_ext varchar(20), splieform_ID varchar(40))")
        break

    for rec in inrec:
        index = index + 1
        record = gpa_parser(rec, outfile, index, record)
        if index == 5000:
            new_record = tuple(record)
            insert_into_db(conn,new_record)
            index = 0
            record = []

    conn.close()


