#!/usr/bin/env python

import os
import sys
import re
import FtpDownload
import Zipper
from collections import defaultdict
from ftplib import FTP
from os.path import basename
import shutil

def parse(infile, ConfigParam=defaultdict):

    date_regex = ConfigParam['ftp_date']
    file_start_regex = ConfigParam['ftp_file_start']
    work_dir = ConfigParam['workdir']
    t1_input_file = None

    if (re.match(date_regex,infile)) or (re.match('current', infile, re.IGNORECASE)):

        try:
            ftp = FTP(ConfigParam['ftp_host'])
        except:
            print 'Oops! FTP_HOST parameter has not been set correctly in the config file.'
            sys.exit()

        ftp.login()

        if infile == 'current':
            try:
                remote_dir = ConfigParam['ftp_curr_path']
                remote_dir = remote_dir.rstrip('/')
            except:
                print 'Oops! FTP Download directory path not set correctly in config file.'
                sys.exit()
        else:
            [month,year] = infile.split('_')
            month = month.capitalize()
            try:
                remote_dir = ConfigParam['ftp_old_path']
                remote_dir = remote_dir.rstrip('/')
            except:
                print 'Oops! FTP Download directory path not set correctly in config file.'
                sys.exit()

        [download_status,down_filename] = FtpDownload.download(infile,ftp, remote_dir, work_dir)
        if download_status == 1:
            t1_input_file = Zipper.unzipper(down_filename, ConfigParam)
        elif download_status == -1:
            if re.search('.gz', down_filename):
                t1_input_file = Zipper.unzipper(down_filename, ConfigParam)
            else:
                t1_input_file = down_filename
    else:
        input_basename = basename(infile)

        if os.path.exists(work_dir + '/' + input_basename):
            t1_input_file = input_basename
        elif os.path.exists(infile):
            shutil.move(infile,work_dir)
            t1_input_file = basename(infile)
        else:
            print infile + ' is not available.'
            sys.exit(1)

        if re.search('\.gz$',t1_input_file):
            extracted_file = t1_input_file.replace('.gz','')
            if os.path.exists(work_dir + '/' + extracted_file):
                t1_input_file = ''
                t1_input_file = extracted_file
            elif os.path.exists(extracted_file):
                shutil.move(extracted_file,work_dir)
                t1_input_file = ''
                t1_input_file = extracted_file
            else:
                extracted_file = Zipper.unzipper(t1_input_file, ConfigParam)
                t1_input_file = ''
                t1_input_file = extracted_file

        #Add the Format Checker Module
    return t1_input_file


def parse_cafa(infile, ConfigParam=defaultdict()):

    work_dir = ConfigParam['workdir']
    input_basename = basename(infile)

    if os.path.exists(work_dir + '/' + input_basename):
        t1_input_file = input_basename
    elif os.path.exists(infile):
        shutil.move(infile,work_dir)
        t1_input_file = basename(infile)
    else:
        print infile + ' is not available.'
        sys.exit(1)

    infile_handle = open(work_dir + '/' + t1_input_file, 'r')

    outfile = t1_input_file + '.iea1'
    outfile_handle = open(work_dir + '/' + outfile, 'w')

    if t1_input_file.endswith('.fasta'):
        for lines in infile_handle:
            if lines[0] == '>':
                cafa_id = lines.strip().split(' ')[0]
                header = lines.strip().split(' ')[1]
                target_prot = header.replace('(', '').replace(')', '')
                print >> outfile_handle, cafa_id + '\t' + target_prot

    else:
        for lines in infile_handle:
            print >> outfile_handle, lines

    outfile_handle.close()
    infile_handle.close()

    return t1_input_file

if __name__ == '__main__':
    parse(infile)
