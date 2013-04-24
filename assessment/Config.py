#!/usr/bin/python

import os
import sys
import re

def create():

    outfile_handle = open('.cafarc', 'w')
    outfile_handle.write('[WORKDIR]\n')
    
    work_dir_response = raw_input('Provide a path to your working directory (If left blank, defaults  to current directory) : ')
    if work_dir_response == '':
        outfile_handle.write('DEFAULT_PATH : .\n') 
    elif work_dir_response.startswith('.') or work_dir_response.startswith('/'):
        outfile_handle.write('DEFAULT_PATH : ' + work_dir_response + '\n')
    else:
        outfile_handle.write('DEFAULT_PATH : ' + './' + work_dir_response + '\n')
        
if __name__ == '__main__':
    create()
