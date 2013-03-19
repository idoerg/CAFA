#!/usr/bin/python

import os
import sys
import re
import uniprot_ftp
import Zipper
from collections import defaultdict

def parse(infile, ConfigParam=defaultdict):

    date_regex = ConfigParam['ftp_date']
    file_start_regex = ConfigParam['ftp_file_start']

    if (re.match(date_regex,infile)) or (re.match(ConfigParam['ftp_curr_path'], infile, re.IGNORECASE)):
        [download_status,down_filename] = uniprot_ftp.download(infile, ConfigParam)
        if download_status == 1:
            t1_input_file = Zipper.unzipper(down_filename, ConfigParam)
        elif download_status == -1:
            if re.search('.gz', down_filename):
                t1_input_file = Zipper.unzipper(down_filename, ConfigParam)
            else:
                t1_input_file = down_filename
    else:
        t1_input_file = infile

    return t1_input_file

if __name__ == '__main__':
    parse(infile)
