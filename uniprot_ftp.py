#!/usr/bin/python

import os
import sys
import re
import shutil
from ftplib import FTP
import progressbar
from collections import defaultdict

def download(time_point, ConfigParam=defaultdict()):

    filename = ''
    file_list = []
    download_status = 0
    filename = ''

    try:
        work_dir = ConfigParam['workdir']
    except:
        print 'Oops! The working directory parameter is not set properly in the config file.'
        sys.exit()

    try:
        ftp = FTP(ConfigParam['ftp_host'])
    except:
        print 'Oops! FTP_HOST parameter has not been set correctly in the config file.'
        sys.exit()

    ftp.login()
    print 'Logged into FTP'
    
    if time_point == 'current':
        try:
            remote_dir = ConfigParam['ftp_curr_path'] 
        except:
            print 'Oops! FTP Download directory path not set correctly in config file.'
            sys.exit()
    else:
        [month,year] = time_point.split('_')
        month = month.capitalize()
        try:
            remote_dir = ConfigParam['ftp_old_path']
        except:
            print 'Oops! FTP Download directory path not set correctly in config file.'
            sys.exit()

    ftp.cwd(remote_dir)
    ftp.dir('.', file_list.append)


    if time_point == 'current':
        for i in file_list:
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            unzipped_fname = terms[-1].replace('.gz', '')
            if os.path.exists(work_dir + '/' + terms[-1]):
                filename = terms[-1]
                download_status = -1
                continue
            elif os.path.exists(work_dir + '/' + unzipped_fname):
                filename = unzipped_fname
                download_status = -1
                continue
            filename = terms[-1]
            filesize = ftp.size(filename)
        local_filename = os.path.join(work_dir + '/' + filename)
        progress = progressbar.AnimatedProgressBar(start=0, end=filesize, width=50)
        print 'Downloading ' + filename
        with open(local_filename, 'w') as outfile:
            def callback(block):
                outfile.write(block)
                progress + len(block)
                progress.show_progress()
  
            ftp.retrbinary('RETR '+filename, callback)
        download_status = 1

    else:
        for i in file_list:
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            if(terms[18] == month) and (terms[21] == year):
                unzipped_fname = terms[-1].replace('.gz', '')
                if os.path.exists(work_dir + '/' + terms[-1]):
                    filename = terms[-1]
                    download_status = -1
                    continue
                elif os.path.exists(work_dir + '/' + unzipped_fname):
                    filename = unzipped_fname
                    download_status = -1
                    continue
                
                if filename:
                    version_num = filename.split('.')[2]
                    if terms[-1].split('.')[2] > version_num:
                        filename = terms[-1]
                        filesize = ftp.size(filename)
                else:
                    filename = terms[-1]
                    filesize = ftp.size(filename)

        if download_status == 0:
            local_filename = os.path.join(work_dir + '/' + filename)
            progress = progressbar.AnimatedProgressBar(start=0, end=filesize, width=50)
                
            print 'Downloading ' + filename
            with open(local_filename, 'w') as outfile:
                def callback(block):
                    outfile.write(block)
                    progress + len(block)
                    progress.show_progress()
  
                ftp.retrbinary('RETR '+filename, callback)
            download_status = 1

    if download_status == 1:
        print '\nSuccesfully downloaded files from uniprot-goa'
    elif download_status == -1:
        print '\nFile to be downloaded already present in working directory'
    else:
        print '\nThere is no file to be downloaded in the specified time point'
        time_point = raw_input('Do you want to provide a different time point (either provide a time point or say no) : ')
        if (re.match('[a-zA-Z]+\_\d+',time_point)) or (re.match('current',time_point)):
            connect(time_point)
        elif time_point == 'no':
            sys.exit(1)

    return download_status, filename

if __name__ == '__main__':
    time_point = sys.argv[1]
    #ConfigParam = {'ftp_host' : 'ftp.ebi.ac.uk',
     #              'ftp_curr_path' : 'pub/databases/GO/goa/UNIPROT',
      #             'ftp_old_path' : 'pub/databases/GO/goa/old/UNIPROT'
       #            }

    download(time_point, ConfigParam)


