#!/usr/bin/env python
# -*- coding: utf-8 -*-
# meta4zenf 
# Copyright 2012 Leo Broska
#
'''
meta4zenf is a tool to clean the metadata of images for upload to
Zenfolio.com. It tackle two issues:

(1) Zenfolio expects the metadata for title and caption without html.
This tool strips the html tags leaving the text intact.
(2) Not all keywords in image metadata are necessarily relevant for a
public gallery on Zenfolio. This tool removes certain keywords from
the Keywords tag.
'''

import argparse
import logging
import os
import sys
from HTMLParser import HTMLParser
import re
import exiftool

class ArgHelpParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        sys.stderr.flush()
        sys.stdout.write(self.format_usage() + 'try --help for more information.\n')
        sys.exit(2)

class ExistingPath(argparse.FileType):
    def __call__(self, string):
        if os.path.exists(string):
            return string
        else:
            message = "path '%s' does not exist"
            raise argparse.ArgumentTypeError(message % (string))

#
# Options
#    
def argParser(locArgs = None):
    parser = ArgHelpParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files',  metavar='FILE', type=ExistingPath("r"), nargs='+',
                        help='file or directory to work on')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', 
                        help='set logging output level to DEBUG')
    return parser.parse_args(locArgs)


#
# The html stripper
#
class HtmlStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        #return ''.join(self.fed)
        
        txt = ""
        for s in self.fed:
            re.sub(r'\s', '', s)
            txt = txt + s
        return txt

def strip_html(html):
    s = HtmlStripper()
    s.feed(html)
    return s.get_data()

def isBackup(fname):
    return fname.endswith("_original")

    
TAGS_FOR_HTML_STRIPPING = ['IPTC:Caption-Abstract','XMP:Description','XMP:Headline']

KEYWORDS_TO_REMOVE = ['published (flickr)', 'lisa', 'mainly-lisa', 'p365contender', 'print-crop', 'family', 'schwester']

EXIF_ERROR_TAG = "ExifTool:Error"
#
# Work Functions
#
def doFile(fname):
    """go trough relevant metadata fields and strip html from them
    plus remove the unwanted keywords."""

    if isBackup(fname):
        logging.debug("skip backup file %s" % fname)
        return
    
    logging.info('working on "%s"', os.path.basename(fname))   

    with exiftool.ExifTool(addedargs=["-m"]) as extl:

        try:
            metadata = extl.get_metadata (fname)
            if EXIF_ERROR_TAG in metadata:
                raise IOError(-99, ('Can\'t read metadata: "%s"' % metadata[EXIF_ERROR_TAG]))
            tagsDict ={}
            for tag in TAGS_FOR_HTML_STRIPPING:
                try:
                    value_stripped = strip_html(metadata[tag])
                    tagsDict[tag] = value_stripped
                except KeyError, e:
                    pass

            extlout = extl.set_tags(tagsDict, fname)
            if not exiftool.check_ok(extlout):
                logging.info(exiftool.format_error(extlout))
            else:
                logging.debug(exiftool.format_error(extlout))            

            extlout = extl.set_keywords(exiftool.KW_REMOVE, KEYWORDS_TO_REMOVE, fname)
            if not exiftool.check_ok(extlout):
                logging.info(exiftool.format_error(extlout))
            else:
                logging.debug(exiftool.format_error(extlout))
        except Exception as e:
            logging.info('Error on file "%s": %s' % (os.path.basename(fname), str(e) ) )



#
# main
#
if __name__ == '__main__':
    
    args = argParser()     
    dbgLevel=logging.INFO

    if args.debug:
        dbgLevel=logging.DEBUG
    logging.basicConfig(format='%(levelname)s: %(message)s', level=dbgLevel, stream=sys.stdout)
            
    for f in args.files:

        if os.path.isdir(f):
            for elem in os.listdir(f):
                path = os.path.join(f, elem)
                doFile(path)
                
        elif os.path.isfile(f):
            doFile(f)
            
