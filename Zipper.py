#!/usr/bin/python

import os
import sys
from collections import defaultdict

def unzipper(infile, ConfigParam=defaultdict()):
    unzip_file = ''
    work_dir = ConfigParam['workdir']

    if not infile == '' :
        print 'Extracting file ' + infile
        os.system('gunzip ' + work_dir + '/' + infile)
        unzip_file = infile.replace('.gz',  '')

    return unzip_file
    

if __name__ == '__main__':
    zip_file = sys.argv[1]
    unzipper(zip_file)
