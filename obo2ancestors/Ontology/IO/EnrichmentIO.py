# Copyright 2013 by Kamil Koziara. All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""
I/O operations for Enrichment.
"""

import csv, string, ast
from .. import Enrichment, EnrichmentEntry
from Interfaces import OntoWriter, OntoReader

def _row_to_entry(row, corr_names, read_attrs):
    oid = row[0]
    name = row[1]
    p_val = float(row[2])
    corrections = {}
    corrlist = row[3].split("|")
    for i in xrange(len(corr_names)):
        corrections[corr_names[i]] = float(corrlist[i])
    entry = EnrichmentEntry(oid, name, p_val)
    entry.corrections = corrections
    if read_attrs and row[4]:
        entry.attrs = ast.literal_eval(row[4])
    return entry

class EnrichmentReader(OntoReader):
    """
    Class for reading an enrichment from a file.
    """

    def __init__(self, file_handle, read_attrs = True):
        self._handle = file_handle
        self._read_attrs = read_attrs

    def read(self):
        try:
            writer = csv.reader(self._handle, delimiter = '\t')
            row = writer.next()
            method = row[0][1:].strip()
            row = writer.next()
            nums = row[0].split()
            entries_num = int(nums[1])
            warnings_num = int(nums[2])
            row = writer.next()
            corr_names = row[3].split("|")
            entries = []
            for _ in xrange(entries_num):
                entries.append(_row_to_entry(writer.next(), corr_names, self._read_attrs))
            warnings = []
            for _ in xrange(warnings_num):
                warnings.append(writer.next()[1])
            return Enrichment(method, entries, warnings, corr_names)

        except StopIteration:
            raise Exception("Error while reading: Enrichment file not valid.")

def _entry_to_row(entry, corr_names, write_attrs):
    corr_string = string.join([str(entry.corrections[x]) for x in corr_names], "|")
    return [entry.id, entry.name, entry.p_value, corr_string, entry.attrs]

class EnrichmentWriter(OntoWriter):
    """
    Class for writing an enrichment to a file.
    """

    def __init__(self, file_handle, write_attrs = True):
        self._handle = file_handle
        self._write_attrs = write_attrs

    def write(self, enrichment):
        writer = csv.writer(self._handle, delimiter = '\t')
        writer.writerow(["# " + enrichment.method])
        writer.writerow(["# " + str(len(enrichment.entries)) + " " + str(len(enrichment.warnings))])
        writer.writerow(["id", "name", "p-value", string.join(enrichment.corrections, "|"), "attributes"])
        for entry in enrichment.entries:
            writer.writerow(_entry_to_row(entry, enrichment.corrections, self._write_attrs))
        for warning in enrichment.warnings:
            writer.writerow(["!", warning])
