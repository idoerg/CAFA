#!/usr/bin/env python
#
# Command line interface for the obo2ancestors script that allows you to take an
# obo file and list the ancestors of every term within the file.
#
# @author Andrew Oberlin
# @date Wednesday, 11, 2014
#
import sys
import argparse
import urllib2
from collections import defaultdict
#import progressbar
from oboparser import OBOparser, TypeDefNode

class Obo2Ancestors:
    VERBOSE = False
    WEB = False

    def __init__(self, input, verbose=False, web=False):
        self.VERBOSE = verbose
        self.WEB = web
        self.input = input
        self.stream = None

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
        if self.WEB: self.wget(self.input)

        self.stream = open(self.input, 'r')

    def close(self):
        self.stream.close()

    def __call__(self):
        '''
            Parse the data from the obo file using the class in biopython for reading obo files. Creates
            a dictionary containing a mapping from accession to ancestors in order from most immediate
            to most distant.
        '''
        children = defaultdict(set)
        ancestors = defaultdict(list)

        with self as stream:
            parser = OBOparser()
            ontology = parser.createOntologyFromOBOFile(stream)

            # the ontology object does not track roots or "leaves" or anything so
            # we have to go through each node and keep an open list
            for term in ontology.terms:
                if not isinstance(term, TypeDefNode) and term.isA:
                    ancestors[term.id].extend([term.isA])
                    children[term.isA].add(term.id)

            # Go through all the terms that do not have ancestors in the children list
            # and treat them as the roots of the DAG. Trickle down the parenthood from there.
            roots = set(children.keys()) - set(ancestors.keys())

            # recursive method for trickle down
            def recurse(root):
                if not children[root]: return

                for child in children[root]:
                    ancestors[child].extend(ancestors[root])
                    recurse(child)

            for root in roots:
                recurse(root)

        return ancestors

    def wget(url):
        handle = urllib2.urlopen(url)
        Obo2Ancestors.chunk_read(handle, verbose=self.VERBOSE)

    @staticmethod
    def chunk_read(handle, chunk_size=8192, verbose=False):
        total_size = response.info().getheader('Content-Length').strip()
        try:
            total_size = int(total_size)
        except ValueError:
            total_size = None
            if verbose: print "Could not find content length for indicated file..."
        bytes_so_far = 0

        bar, out = None, None
        if verbose and total_size:
            bar = progressbar.ProgressBar(maxval=total_size, \
                widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
            bar.start()
        elif verbose and not total_size: # could not determine total size, but want verbosity
            out = 0
        '''
        with open( + ) as fp:
            while 1:
                chunk = response.read(chunk_size)
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
        '''
        return outfile_name




if __name__ == '__main__':
    # create the argument parser for this CLI
    parser = argparse.ArgumentParser(prog='obo2ancestors',
        description='Parses an obo file and creates a file listing the ancestors of each GO accession')

    # setup the arguments for the argparser
    parser.add_argument('obo', help='The obo file to parse or a URL to an obo file if -w is used')
    parser.add_argument('-w', '--web', action='store_true', default=False,
        help='Should the obo file be downloaded from the web as a URL')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)

    # setup the output source
    parser.add_argument('-o', '--output',
        help='''The name of the file into which the results should be piped.
        Use "-" to indicate the use of standard out''', default="-")

    # parse the arguments for this CLI
    args = parser.parse_args()
    obo2ancestors = Obo2Ancestors(args.obo, args.verbose, args.web)

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
