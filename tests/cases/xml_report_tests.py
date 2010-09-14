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
from core.modules.XmlReportGenerator import XmlReportGenerator

try:
	from lxml import etree
except ImportError:
	raise MomError( "Fatal: lxml package missing, required for Xml transformations" )

class XmlReportTests( MomBuildMockupTestCase ):

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self )

	def _runBuild( self ):
		self.build.runPreFlightChecks()
		self.build.runSetups()
		self.build.buildAndReturn()

	def testCreateXmlReport( self ):
		self._runBuild()
		report = XmlReport( self.build )
		report.prepare()

		xmlString = report.getReport()
		doc = etree.XML( xmlString )

		self.assertEqual( doc.tag, "build" ) # root
		self.assertNotEquals( doc.find( './/project' ), None )
		self.assertNotEquals( doc.find( './/environment' ), None )

		self.assertNotEquals( doc.find( './/plugin' ), None )
		self.assertNotEquals( doc.find( './/step' ), None )
		self.assertNotEquals( doc.find( './/action' ), None )

		self.assertNotEquals( doc.find( './/plugin[@name="CMakeBuilder"]' ), None )

	def testConvertXmlReportToHtml( self ):
		self._runBuild()

		report = XmlReport( self.build )
		report.prepare()
		converter = XmlReportConverter( report )

		xmlString = converter.convertToHtml()
		doc = etree.XML( xmlString )

		# TODO: Add more _useful_ tests 
		self.assertEqual( doc.tag, "{http://www.w3.org/1999/xhtml}html" ) # root
		self.assertNotEquals( doc.find( ".//{http://www.w3.org/1999/xhtml}table" ), None )
		self.assertNotEquals( doc.find( ".//{http://www.w3.org/1999/xhtml}td" ), None )


	def testConvertXmlReportToText( self ):
		self._runBuild()

		report = XmlReport( self.build )
		report.prepare()
		converter = XmlReportConverter( report )

		text = converter.convertToText()

		# TODO: Add more _useful_ tests 
		self.assertTrue( len( text ) > 1000 )

	def testXmlReportGenerator( self ):
		generator = XmlReportGenerator()
		self.build.addPlugin( generator )
		self._runBuild()

		report = XmlReport( self.build )
		report.prepare()
		reportContent = report.getReport()

		filePath = generator.getReportFile()
		self.assertNotEquals( filePath, None, "Log file does not exist" )

		f = open( filePath )
		fileContent = f.read()
		self.assertNotEqual( len( fileContent ), 0, "Log file is empty" )

		self.assertEqual( fileContent, reportContent, "Report file content not written correctly" )


if __name__ == "__main__":
	unittest.main()
