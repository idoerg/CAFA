#!/usr/bin/python

import os
import sys
import re
from collections import defaultdict
import subprocess
import stat

def check(infile1, infile2, mode):
    if mode == 'T':
        if os.stat(infile1).st_size == 0:
            print 'You have submitted an empty t1 file.'
            sys.exit(1)
        elif re.match('\S+\.fasta$', infile1):
            pattern = '>'
            outfile = open('tmp.txt', 'w')
            subprocess.call(['grep', pattern, infile1], stdout=outfile)
            if not os.stat('tmp.txt').st_size > 0:
                print 'Probably incorrect format for fasta file.'
                sys.exit(1)
        else:
            sys.exit(1)

        if os.stat(infile2).st_size == 0:
            print 'You have submitted an empty t2 file.'
            sys.exit(1)
        else:
            infile2_handle = open(infile2, 'r')
            firstline = infile2_handle.readline()
            fields = firstline.strip().split('\t')
            if re.search('^\!gaf', firstline):
                pass
            elif len(fields) == 15:
                pass
            else:
                print "Error in input1 file format"
                sys.exit(1)

        
    elif mode == 'F':
        if os.stat(infile1).st_size == 0:
            print 'You have submitted an empty t1 file.'
            sys.exit(1)
        else:
            infile1_handle = open(infile1, 'r')
            firstline = infile1_handle.readline()
            fields = firstline.strip().split('\t')
            if re.search('^\!gaf', firstline):
                pass
            elif len(fields) == 15:
                pass
            else:
                print "Error in input1 file format"
                sys.exit(1)

        if os.stat(infile2).st_size == 0:
            print 'You have submitted an empty t2 file.'
            sys.exit(1)
        else:
            infile2_handle = open(infile2, 'r')
            firstline = infile2_handle.readline()
            fields = firstline.strip().split('\t')
            if re.search('^\!gaf', firstline):
                pass
            elif len(fields) == 15:
                pass
            else:
                print "Error in input1 file format"
                sys.exit(1)
        
        


if __name__ == '__main__':
    infile1 = sys.argv[1]
    infile2 = sys.argv[2]
    mode = 'F'
    check(infile1, infile2, mode)
