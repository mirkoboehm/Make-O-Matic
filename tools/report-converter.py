#!/usr/bin/env python

from __future__ import print_function
from core.helpers.XmlReportConverter import XmlReportConverter
from core.helpers.XmlReport import StringBasedXmlReport
from core.MApplication import MApplication
import sys
from xml.dom.minidom import Document, parseString

TARGET_FORMATS = ["text", "html"]

def usage():
	print_stderr( "Usage: {0} INPUT_FILE [text|html]".format( sys.argv[0] ) )

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
		sys.exit( 1 )

	# check if second parameter in TARGET_FORMATS, if unset: use text
	try:
		if sys.argv[2] in TARGET_FORMATS:
			targetFormat = sys.argv[2]
		else:
			usage()
			sys.exit( 1 )
	except IndexError:
		targetFormat = "text"

	# start IO
	fin = open( inputFile )
	xmlReport = StringBasedXmlReport( fin.read() )
	fin.close

	converter = XmlReportConverter( xmlReport )
	if targetFormat == "text":
		print( converter.convertToTextSummary() )
		print( converter.convertToText() )
	elif targetFormat == "html":
		print( converter.convertToHtml() )

if __name__ == "__main__":
	main()
