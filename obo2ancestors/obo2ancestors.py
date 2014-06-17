#!/usr/bin/env python
#
# Command line interface for the obo2ancestors script that allows you to take an
# obo file and list the ancestors of every term within the file.
#
# @author Andrew Oberlin
# @date Wednesday, 11, 2014
#
import os, sys
import argparse
import urllib2
from collections import defaultdict
from Ontology.IO.OboIO import OboReader
import tempfile

class OboRetriever:
    VERBOSE = False
    KEEP = None

    def __init__(self, url, keep=None, verbose=False):
        self.VERBOSE = verbose
        self.KEEP = keep
        self.url = url
        self.filename = None

    def wget(self):
        handle = urllib2.urlopen(self.url)
        self.filename = OboRetriever.chunk_read(handle, verbose=self.VERBOSE)
        return self.filename

    @staticmethod
    def chunk_read(handle, chunk_size=8192, verbose=False):
        total_size = handle.info().getheader('Content-Length').strip()
        try:
            total_size = int(total_size)
        except ValueError:
            total_size = None
            if verbose: print "Could not find content length for indicated file..."
        bytes_so_far = 0

        if verbose:
            print "Downloading the file from the web. This may take a minute..."

        bar, out = None, None
        if verbose and total_size:
            import progressbar
            bar = progressbar.ProgressBar(maxval=total_size, \
                widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
            bar.start()
        elif verbose and not total_size: # could not determine total size, but want verbosity
            out = 0

        fp = tempfile.NamedTemporaryFile(delete=False)
        with fp:
            while 1:
                chunk = handle.read(chunk_size)
                fp.write(chunk)
                bytes_so_far += len(chunk)

                if not chunk:
                    break

                if bar:
                    bar.update(bytes_so_far)
                elif out is not None:
                    prefix = '\r' if out > 0 else ''
                    print prefix + "Downloaded a total of {0} bytes of 'Unknown' bytes".format(bytes_so_far)
                    out += 1

            bar.finish()

        return fp.name

    def cleanup(self):
        if self.filename:
            if self.KEEP:
                os.rename(self.filename, os.path.join(self.KEEP))
            else:
                os.remove(self.filename)

class Obo2Ancestors:
    VERBOSE = False

    def __init__(self, input, verbose=False):
        self.input = input
        self.stream, self.name = None, None
        self.VERBOSE = verbose

    # support for "with" keyword
    def __enter__(self):
        self.open()
        return self.stream

    def __exit__(self, type, value, traceback):
        self.close()

    def open(self):
        '''
            Opens the stream for the input and downloads the input file if necessary.
        '''
        if self.stream: return # the stream as already been opened

        # downloads the file from the internet and sets the self.input to point to the
        # downloaded file
        self.name = self.input
        if isinstance(self.input, OboRetriever):
            self.name = self.input.wget()

        self.stream = open(self.name, 'r')

    def close(self):
        self.stream.close()
        self.stream = None
        if isinstance(self.input, OboRetriever):
            self.input.cleanup()

    def __call__(self):
        '''
            Parse the data from the obo file using the class in biopython for reading obo files. Creates
            a dictionary containing a mapping from accession to ancestors in order from most immediate
            to most distant.
        '''
        ancestors = defaultdict(list)

        with self as stream:
            if self.VERBOSE:
                print "Parsing the OBO file into an ontology..."
            parser = OboReader(stream)
            ontology = parser.read()

            if self.VERBOSE:
                print "Analyzing the ontology..."
            for node in ontology.nodes:
                ancestors[node] = ontology.get_ancestors(node)

        return ancestors


if __name__ == '__main__':
    # create the argument parser for this CLI
    parser = argparse.ArgumentParser(prog='obo2ancestors',
        description='Parses an obo file and creates a file listing the ancestors of each GO accession')

    # setup the arguments for the argparser
    parser.add_argument('obo', help='The obo file to parse or a URL to an obo file if -w is used')
    parser.add_argument('-w', '--web', action='store_true', default=False,
        help='Should the obo file be downloaded from the web as a URL')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-k', '--keep',
        help='''Optional. Used in junction with the "w" option only. The name of the place to store
        the obo file once downloaded. Should include the name of the file. i.e. tmp/go.obo''',
        default=None)

    # setup the output source
    parser.add_argument('-o', '--output',
        help='''The name of the file into which the results should be piped.
        Use "-" to indicate the use of standard out.''', default="-")

    # parse the arguments for this CLI
    args = parser.parse_args()
    obo2ancestors = Obo2Ancestors(args.obo if not args.web else OboRetriever(args.obo, args.keep, args.verbose), args.verbose)

    try:
        outstream = sys.stdout if args.output == "-" else open(args.output, 'w') # python 2.x
    except IOError:
        # could not open the file reverting to the standard out
        if obo2Ancestors.VERBOSE: print "Could not open the target file for output. Defaulting to standard out..."
        outstream = sys.stdout

    # pass these parameters to the main function
    for go, ancestors in obo2ancestors().iteritems():
        outstream.write(go + "\t" + ",".join(ancestors) + "\n")

    outstream.close()
