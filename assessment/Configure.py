#!/usr/bin/env python

import os
import sys
import re

'''
   The assessment program first requires a mapping file to be downloaded into 
   the current directory.

   This is the first script to be run in the assessment section.
   This script downloads the latest version of the id-mapping file from uniprot
   that will be used later in the main assessment program.
'''


print 'Downloading mapping file from UniProt'
os.system('wget -q ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/' + \
              'knowledgebase/idmapping/idmapping_selected.tab.gz')
os.system('gunzip idmapping_selected.tab.gz')
