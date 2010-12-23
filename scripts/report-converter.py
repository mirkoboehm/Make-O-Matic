#!/usr/bin/env python

from __future__ import print_function
from core.helpers.XmlReportConverter import XmlReportConverter
from core.helpers.XmlReport import XmlReport
from core.MApplication import MApplication
import sys
from xml.dom.minidom import Document, parseString

def usage():
	print_stderr( "Usage: {0} INPUT_FILE".format( sys.argv[0] ) )

def print_stderr( message ):
	print( message, file = sys.stderr )

def main():
	# instantiate MApplication, required for debug() calls
	app = MApplication()

	# check if first parameter is set
	try:
		inputFile = sys.argv[1]
	except IndexError:
		usage()
		return 1

	# start IO
	fin = open( inputFile )
	xmlReport = XmlReport( fin.read() )
	fin.close

	# start converting
	converter = XmlReportConverter( xmlReport )
	print( converter.convertToText() )

if __name__ == "__main__":
	main()
