# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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

import unittest
from core.Exceptions import MomError
from core.modules.reporters.XmlReport import XmlReport
from core.helpers.XmlReportConverter import XmlReportConverter
from core.modules.XmlReportGenerator import XmlReportGenerator
from tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings

try:
	from lxml import etree
except ImportError:
	raise MomError( "Fatal: lxml package missing, required for Xml transformations" )

class XmlReportTests( MomBuildMockupTestCase ):

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self, useEnvironments = True )

	def _build( self, type = 'm' ):
		mApp().getSettings().set( Settings.ScriptLogLevel, 2 )
		mApp().getSettings().set( Settings.ProjectBuildType, type )

		#self.build.addLogger( ConsoleLogger() )
		self.build.runPreFlightChecks()
		self.build.runSetups()
		self.build.buildAndReturn()

	def getXmlReport( self ):
		report = XmlReport( self.build )
		report.prepare()
		return report

	def testCreateXmlReport( self ):
		self._build()
		doc = etree.XML( self.getXmlReport().getReport() )

		self.assertEqual( doc.tag, "build" ) # root
		self.assertNotEquals( doc.find( './/project' ), None )
		self.assertNotEquals( doc.find( './/environments' ), None )
		self.assertNotEquals( doc.find( './/configuration' ), None )
		self.assertNotEquals( doc.find( './/plugin' ), None )
		self.assertNotEquals( doc.find( './/step' ), None )
		self.assertNotEquals( doc.find( './/action' ), None )

		self.assertNotEquals( doc.find( './/plugin[@name="CMakeBuilder"]' ), None )

	def testEnvironmentExpand( self ):
		# TODO: FIXME: This test fails for some reason

		self._build( 'c' )
		doc = etree.XML( self.getXmlReport().getReport() )

		self.assertNotEquals( doc.find( './/environments/environment' ), None, "Did not find matching environments" )

	def testNoEnvironmentExpand( self ):
		self._build( 'm' )
		doc = etree.XML( self.getXmlReport().getReport() )

		self.assertNotEquals( doc.find( './/environments/configuration' ), None, )

	def testConvertXmlReportToHtml( self ):
		self._build()
		converter = XmlReportConverter( self.getXmlReport() )
		xmlString = converter.convertToHtml()
		doc = etree.XML( xmlString )

		# TODO: Add more _useful_ tests 
		self.assertEqual( doc.tag, "{http://www.w3.org/1999/xhtml}html" ) # root
		self.assertNotEquals( doc.find( ".//{http://www.w3.org/1999/xhtml}table" ), None )
		self.assertNotEquals( doc.find( ".//{http://www.w3.org/1999/xhtml}td" ), None )

	def testConvertXmlReportToText( self ):
		self._build()
		converter = XmlReportConverter( self.getXmlReport() )
		text = converter.convertToText()

		# TODO: Add more _useful_ tests
		self.assertTrue( len( text ) > 1000 )

	def testXmlReportGenerator( self ):
		generator = XmlReportGenerator()
		self.build.addPlugin( generator )
		self._build()

		reportContent = self.getXmlReport().getReport()
		filePath = generator.getReportFile()

		self.assertNotEquals( filePath, None, "Log file does not exist" )

		# check file content
		file = open( filePath )
		fileContent = file.read()
		self.assertNotEqual( len( fileContent ), 0, "Log file is empty" )

		self.assertEqual( fileContent, reportContent, "Report file content not written correctly" )

if __name__ == "__main__":
	unittest.main()
