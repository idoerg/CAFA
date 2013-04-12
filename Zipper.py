#!/usr/bin/python

import os
import sys
from collections import defaultdict

def unzipper(infile, ConfigParam=defaultdict()):
    unzip_file = ''
    work_dir = ConfigParam['workdir']

    if not infile == '' :
        unzip_file = infile.replace('.gz',  '')
        print 'Extracting file ' + infile
        #os.system('gunzip -c ' + work_dir + '/' + infile + ' > ' + work_dir + '/' + unzip_file)
        os.system('gunzip ' + work_dir + '/' + infile)

    return unzip_file
    

if __name__ == '__main__':
    zip_file = sys.argv[1]
    unzipper(zip_file)
