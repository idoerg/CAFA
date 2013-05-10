#!/usr/bin/python

import os
import sys
import re
import shutil
import progressbar
from collections import defaultdict
import multiprocessing

def download(time_point,ftp,remote_dir,work_dir):

    filename = ''
    file_list = []
    download_status = 0
    filename = ''
    file_found = 0

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
            elif os.path.exists('./' + terms[-1]):
                filename = terms[-1]
                download_status = -1
                continue
            elif os.path.exists(work_dir + '/' + unzipped_fname):
                filename = unzipped_fname
                download_status = -1
                continue
            elif os.path.exists('./' + unzipped_fname):
                filename = unzipped_fname
                download_status = -1
                continue
            
            filename = terms[-1]
            filesize = ftp.size(filename)
            file_found = 1

        if download_status == 0 and file_found == 1:
            modified_filesize = float(filesize / 1024000000)
        #if modified_filesize > 1.0:
         #   print 'This is a ' + str(modified_filesize) + ' GB file. Downloading it might take a while. Please be patient!!!'
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

    else:
        for i in file_list:
            [month,year] = time_point.split('_')
            month = month.capitalize()
            terms = i.split(' ')
            if not terms[-1].startswith('gene_association'):
                continue
            if(terms[18] == month) and (terms[21] == year):
                file_found = 1
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

        if download_status == 0 and file_found == 1:
            modified_filesize = float(filesize / 1024000000)
            #if modified_filesize > 1.0:
             #   print 'This is a ' + str(modified_filesize) + ' GB file. Downloading it might take a while. Please be patient!!!'
            
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

    if download_status == 1:
        print '\nSuccesfully downloaded files from uniprot-goa'
    elif download_status == -1:
        print '\n' + time_point + ' file to be downloaded already present in working directory'
    else:
        print '\nThere is no file to be downloaded for time point ' + time_point
        print 'Check out the different time points from this site : ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/old/UNIPROT/'
        time_point = raw_input('Do you want to provide a different time point (either provide a time point or say n) : ')
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


