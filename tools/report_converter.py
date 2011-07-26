#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Make-O-Matic.
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
# 
# Make-O-Matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Make-O-Matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
from mom.core.helpers.XmlReportConverter import XmlReportConverter
from mom.core.helpers.XmlReport import StringBasedXmlReport
from mom.core.MApplication import MApplication
import sys

TARGET_FORMATS = ["text", "text_summary", "html", "html_summary"]

def usage():
	print_stderr( "Usage: {0} INPUT_FILE [{1}]".format( sys.argv[0], "|".join( TARGET_FORMATS ) ) )

def print_stderr( message ):
	print( message, file = sys.stderr )

def main():
	# instantiate MApplication, required for debug() calls
	MApplication()

	# check if first parameter is set
	try:
		inputFile = sys.argv[1]
	except IndexError:
		usage()
		sys.exit( 1 )

	# check if second parameter in TARGET_FORMATS
	try:
		if sys.argv[2] in TARGET_FORMATS:
			targetFormat = sys.argv[2]
		else:
			usage()
			sys.exit( 1 )
	except IndexError:
		# second parameter not set => using default
		targetFormat = "text"

	# start IO
	fin = open( inputFile )
	xmlReport = StringBasedXmlReport( fin.read() )
	fin.close

	converter = XmlReportConverter( xmlReport )
	if targetFormat == "text":
		print( converter.convertToText() )
	elif targetFormat == "text_summary":
		print( converter.convertToTextSummary() )
	elif targetFormat == "html":
		print( converter.convertToHtml( enableCrossLinking = True ) )
	elif targetFormat == "html_summary":
		print( converter.convertToHtml( summaryOnly = True, enableCrossLinking = True ) )

if __name__ == "__main__":
	main()
