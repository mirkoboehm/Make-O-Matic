# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
# 
# make-o-matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# make-o-matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from core.modules.reporters.XmlReport import XmlReport
from tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase
from core.helpers.XmlReportConverter import XmlReportConverter
from core.Exceptions import MomError

try:
	from lxml import etree
except ImportError:
	raise MomError( "Fatal: lxml package missing, required for Xml transformations" )

class XmlReportTests( MomBuildMockupTestCase ):

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self )

		# start build
		self.build.runPreFlightChecks()
		self.build.runSetups()
		self.build.buildAndReturn()

	def testCreateXmlReport( self ):
		report = XmlReport( self.build )
		report.prepare()

		xmlString = report.getReport()
		doc = etree.XML( xmlString )

		self.assertEqual( doc.tag, "build" ) # root
		self.assertIsNotNone( doc.find( './/project' ) )
		self.assertIsNotNone( doc.find( './/environment' ) )

		self.assertIsNotNone( doc.find( './/plugin' ) )
		self.assertIsNotNone( doc.find( './/step' ) )
		self.assertIsNotNone( doc.find( './/action' ) )

		self.assertIsNotNone( doc.find( './/plugin[@name="CMakeBuilder"]' ) )

	def testConvertXmlReportToHtml( self ):
		report = XmlReport( self.build )
		report.prepare()
		converter = XmlReportConverter( report )

		xmlString = converter.convertToHtml()
		doc = etree.XML( xmlString )

		# TODO: Add more _useful_ tests 
		self.assertEqual( doc.tag, "{http://www.w3.org/1999/xhtml}html" ) # root
		self.assertIsNotNone( doc.find( ".//{http://www.w3.org/1999/xhtml}table" ) )
		self.assertIsNotNone( doc.find( ".//{http://www.w3.org/1999/xhtml}td" ) )

	def testConvertXmlReportToText( self ):
		report = XmlReport( self.build )
		report.prepare()
		converter = XmlReportConverter( report )

		text = converter.convertToText()

		# TODO: Add more _useful_ tests 
		self.assertGreater( len( text ), 1000 )

		# debug
		#f = open( "/tmp/workfile", 'w' )
		#f.write( converter.convertToText() )

if __name__ == "__main__":
	unittest.main()
