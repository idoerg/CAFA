#!/usr/bin/env python

import os
import sys
import re

print 'Downloading mapping file from UniProt'
os.system('wget -q ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab.gz')
os.system('gunzip idmapping_selected.tab.gz')
