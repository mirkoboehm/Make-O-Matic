#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Make-O-Matic.
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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
from core.helpers.XmlReportConverter import XmlReportConverter
from core.helpers.XmlReport import StringBasedXmlReport
from core.MApplication import MApplication
import sys

TARGET_FORMATS = ["text", "html"]

def usage():
	print_stderr( "Usage: {0} INPUT_FILE [text|html]".format( sys.argv[0] ) )

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
		print( converter.convertToHtml( enableCrossLinking = True ) )

if __name__ == "__main__":
	main()
