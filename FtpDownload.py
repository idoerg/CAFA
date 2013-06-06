#!/usr/bin/env python

import os
import sys
import re
import shutil
import progressbar
from collections import defaultdict
import multiprocessing
from ftplib import FTP

'''
   This script remotely connects to the uniprot-goa site through FTP, 
   and downloads required files. Before downloading, it checks to see
   if the files are already present in the current or working directory.
   If yes, it does not download them again.

   If there is no file in teh time point being requested, the program will
   ask the user to supply a different time point if they wish to, or exit

   A progressbar keeps updating the amount of download completed.

'''

def check(filename, work_dir):
    
    download_status = 0
    
    unzipped_fname = filename.replace('.gz', '')
    if os.path.exists(work_dir + '/' + filename):
        download_status = -1
    elif os.path.exists('./' + filename):
        download_status = -1
    elif os.path.exists(work_dir + '/' + unzipped_fname):
        filename = unzipped_fname
        download_status = -1
    elif os.path.exists('./' + unzipped_fname):
        filename = unzipped_fname
        download_status = -1
    
    return filename, download_status


def download(work_dir, filename, filesize, ftp):
    local_filename = os.path.join(work_dir + '/' + filename)
    progress = progressbar.AnimatedProgressBar(start=0, end=filesize, width=50)
    print 'Downloading ' + filename
    with open(local_filename, 'w') as outfile:
        def callback(block):
            outfile.write(block)
            progress + len(block)
            progress.show_progress()
            
        ftp.retrbinary('RETR '+filename, callback, 81920)
    download_status = 1

    return download_status


def initialize(time_point,ConfigParam):

    file_list = []
    download_status = 0
    filename = ''
    file_found = 0
    filename_set = []
    work_dir = ConfigParam['workdir']

    try:                                                                                                                                  
        ftp = FTP(ConfigParam['ftp_host'])                                                                                               
    except:                                                                                                                               
        print 'Oops! FTP_HOST parameter has not been set correctly in the config file.'                                                  
        sys.exit()                                                                                                                       
    ftp.login()

    if time_point == 'current':                                                                                                              
        try:                                                                                                                             
            remote_dir = ConfigParam['ftp_curr_path']                                                                                    
            remote_dir = remote_dir.rstrip('/')                                                                                          
        except:                                                                                                                          
            print 'Oops! FTP Download directory path not set correctly in config file.'                                                  
            sys.exit()                                                                                                                   
    else:                                                                                                                                
        [month,year] = time_point.split('_')                                                                                                 
        month = month.capitalize()                                                                                                       
        try:                                                                                                                             
            remote_dir = ConfigParam['ftp_old_path']                                                                                     
            remote_dir = remote_dir.rstrip('/')                                                                                          
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
            [filename, download_status] = check(terms[-1], work_dir)
            file_found = 1

        if download_status == 0 and file_found == 1:
            filesize = ftp.size(filename)
            download_status = download(work_dir, filename, filesize)

    else:
        for i in file_list:
            [month,year] = time_point.split('_')
            month = month.capitalize()
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            if(terms[18] == month) and (terms[21] == year):
                [filename, download_status] = check(terms[-1], work_dir)
                filename_set.append(filename)
                file_found = 1
                
        filename_set.sort()        
        filename = filename_set[-1]

        if download_status == 0 and file_found == 1:
            filesize = ftp.size(filename)
            download_status = download(work_dir, filename, filesize, ftp)

    if download_status == 1:
        print '\nSuccesfully downloaded files from uniprot-goa'
    elif download_status == -1:
        print '\n' + time_point + ' file to be downloaded already present in working directory'
    else:
        print '\nThere is no file to be downloaded for time point ' + time_point
        print 'Check out the different time points from this site : ' + \
            'ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/old/UNIPROT/'
        time_point = raw_input('Do you want to provide a different time point ' + \
                                   '(either provide a time point or say n) : ')
        if (re.match('[a-zA-Z]+\_\d+',time_point)) or (re.match('current',time_point)):
            [download_status, filename] = download(time_point,ftp,remote_dir,work_dir)
        elif time_point == 'n':
            sys.exit(1)

            
    return download_status, filename

if __name__ == '__main__':
    time_point = sys.argv[1]
    #ConfigParam = {'ftp_host' : 'ftp.ebi.ac.uk',
     #              'ftp_curr_path' : 'pub/databases/GO/goa/UNIPROT',
      #             'ftp_old_path' : 'pub/databases/GO/goa/old/UNIPROT'
       #            }

    download(time_point, ConfigParam)


