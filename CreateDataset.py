#!/usr/bin/python

import os
import sys
import re
import FtpDownload
import Zipper
from collections import defaultdict
from ftplib import FTP
from os.path import basename

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
            t1_input_file = infile
        else:
            print infile + ' is not available in your working directory.'
            sys.exit(1)

    return t1_input_file


def parse_cafa(infile):

    infile_basename = basename(infile)
    if not os.path.exists(work_dir + '/' + infile_basename):
        print infile + ' is not available in your working directory.'
        sys.exit(1)

    infile_handle = open(infile, 'r')

    outfile = infile + '.iea1'
    outfile_handle = open(outfile, 'w')

    if infile.endswith('.fasta'):
        for lines in infile_handle:
            if lines[0] == '>':
                header = lines.strip().split(' ')[1]
                target_prot = header.replace('(', '').replace(')', '')
                print >> outfile_handle, target_prot

    else:
        for lines in infile_handle:
            print >> outfile_handle, lines

    outfile_handle.close()
    infile_handle.close()

    return outfile

if __name__ == '__main__':
    parse(infile)
