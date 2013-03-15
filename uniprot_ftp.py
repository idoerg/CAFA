#!/usr/bin/python

import os
import sys
import re
import shutil
from ftplib import FTP
import time
import progressbar

def download(time_point):
    if not os.path.exists(time_point):
        os.makedirs(time_point)
    else:
        shutil.rmtree(time_point)
        os.makedirs(time_point)

    filename = ''
    file_list = []
    download_status = 0

    ftp = FTP('ftp.ebi.ac.uk')
    ftp.login()
    print 'Logged into FTP'
    
    if time_point == 'current':
        remote_dir = '/pub/databases/GO/goa/UNIPROT'
    else:
        [month,year] = time_point.split('_')
        month = month.capitalize()
        remote_dir = '/pub/databases/GO/goa/old/UNIPROT'

    ftp.cwd(remote_dir)
    ftp.dir('.', file_list.append)

    if time_point == 'current':
        for i in file_list:
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            filename = terms[-1]
            filesize = ftp.size(filename)
            local_filename = os.path.join('./' + time_point + '/' + filename)
            progress = progressbar.AnimatedProgressBar(start=0, end=filesize, width=50)
            local_filename = os.path.join('./' + time_point + '/' + filename)
            print 'Downloading files from uniprot-goa'
            with open(local_filename, 'w') as outfile:
                def callback(block):
                    outfile.write(block)
                    progress + len(block)
                    progress.show_progress()
  
                ftp.retrbinary('RETR '+filename, callback)
            download_status = 1
            #download_status = download()

    else:
        for i in file_list:
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            if(terms[18] == month) and (terms[21] == year):
                filename = terms[-1]
                filesize = ftp.size(filename)
                local_filename = os.path.join('./' + time_point + '/' + filename)
                progress = progressbar.AnimatedProgressBar(start=0, end=filesize, width=50)
                local_filename = os.path.join('./' + time_point + '/' + filename)
                print 'Downloading files from uniprot-goa'
                with open(local_filename, 'w') as outfile:
                    def callback(block):
                        outfile.write(block)
                        progress + len(block)
                        progress.show_progress()
  
                    ftp.retrbinary('RETR '+filename, callback)
                download_status = 1
                #download_status = download()

    if download_status == 1:
        print '\nSuccesfully downloaded files from uniprot-goa'
    else:
        print '\nThere is no file to be downloaded in the specified time point'
        time_point = raw_input('Do you want to provide a different time point (either provide a time point or say no) : ')
        if (re.match('[a-zA-Z]+\_\d+',time_point)) or (re.match('current',time_point)):
            connect(time_point)
        elif time_point == 'no':
            sys.exit(1)

if __name__ == '__main__':
    time_point = sys.argv[1]
    download(time_point)
    #connect(time_point)


