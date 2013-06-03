#!/usr/bin/env python

import os
import sys
import sqlite3

input_db = sys.argv[1]

def fetch_data(infile,query):

    conn = sqlite3.connect(infile)
    with conn:
        conn.text_factory = str
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

        for row in rows:
            print str(row)

if __name__ == '__main__':
    query = raw_input("Please enter your search query : ")
    fetch_data(input_db, query)
