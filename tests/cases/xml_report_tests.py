# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
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

import unittest
from core.Exceptions import MomError, ConfigurationError, BuildError
from core.helpers.XmlReport import XmlReport
from core.helpers.XmlReportConverter import XmlReportConverter
from core.plugins.reporters.XmlReportGenerator import XmlReportGenerator
from tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
from core.loggers.ConsoleLogger import ConsoleLogger
import os.path
from core.helpers.XmlUtils import xml_compare

try:
	from lxml import etree
except ImportError:
	try:
		# Python 2.5
		import xml.etree.cElementTree as etree
	except ImportError:
		try:
			# Python 2.5
			import xml.etree.ElementTree as etree
		except ImportError:
			try:
				# normal cElementTree install
				import cElementTree as etree
			except ImportError:
				try:
					# normal ElementTree install
					import elementtree.ElementTree as etree
				except ImportError, e:
					raise MomError( "Could not find a suitable XML module: {0}".format( e ) )

class XmlReportTests( MomBuildMockupTestCase ):

	EXCEPTION_LOCATION = "exception"

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self, useEnvironments = True )

	def _build( self, type = 'm' ):
		mApp().getSettings().set( Settings.ScriptLogLevel, 5 )
		mApp().getSettings().set( Settings.ProjectBuildType, type )

		#self.build.addLogger( ConsoleLogger() )
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

		if etree.__name__ == "lxml.etree":
			self.assertNotEquals( doc.find( './/plugin[@name="CMakeBuilder"]' ), None )

	def testEnvironmentExpand( self ):
		self._build( 'c' )
		doc = etree.XML( self.getXmlReport().getReport() )

		self.assertNotEquals( doc.find( './/environments/environment' ), None, "Did not find matching environments" )
		self.assertNotEquals( doc.find( './/environment/configuration' ), None )

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

	def testConvertXmlReportToHtmlWithoutLxml( self ):
		# write a new method implementation
		def hasXsltSupport_new():
			return False

		converter = XmlReportConverter( self.getXmlReport() )
		converter.hasXsltSupport = hasXsltSupport_new # replace method

		xmlString = converter.convertToHtml()
		self.assertTrue( xmlString == None, "If no XSLT support is available, converting to HTML should not work" )

	def testConvertXmlReportToText( self ):
		self._build()
		converter = XmlReportConverter( self.getXmlReport() )
		text = converter.convertToText()

		# TODO: Add more _useful_ tests
		self.assertTrue( len( text ) > 1000 )

	def testConvertXmlReportToTextSummary( self ):
		MomBuildMockupTestCase.setUp( self, useScm = True ) # enable SCM
		self._build()
		converter = XmlReportConverter( self.getXmlReport() )
		text = converter.convertToTextSummary()

		# TODO: Add more useful tests
		self.assertTrue( len( text ) > 100 )

	def testXmlReportGenerator( self ):
		generator = XmlReportGenerator()
		self.build.addPlugin( generator )
		self._build()

		reportContent = self.getXmlReport().getReport()
		filePath = generator.getReportFile()

		self.assertTrue( os.path.exists( filePath ), "Log file does not exist" )

		# check file content
		file = open( filePath )
		fileContent = file.read()
		self.assertNotEqual( len( fileContent ), 0, "Log file is empty" )

#		f1 = open( "/tmp/workfile1", 'w' )
#		f2 = open( "/tmp/workfile2", 'w' )
#		f1.write( reportContent )
#		f2.write( fileContent )

		doc1 = etree.XML( reportContent )
		doc2 = etree.XML( fileContent )

		self.assertTrue( xml_compare( doc1, doc2 ), "Report file content differs from report output" )

	def testXmlReportOnStepFailure( self ):
		self._build()

		def failed_new():
			return True

		step = self.project.getStep( 'build-cleanup' )
		step.failed = failed_new

		converter = XmlReportConverter( self.getXmlReport() )
		logText = converter.convertToFailedStepsLog()

		self.assertTrue( "build-cleanup" in logText )

	def testXmlReportOnException( self ):
		# Covers runSetups phase

		def runSetups_new():
			raise MomError( "Test Error" )

		# inject erroneous method
		self.build.runSetups = runSetups_new

		self._build()
		doc = etree.XML( self.getXmlReport().getReport() )

		e = self.EXCEPTION_LOCATION
		self.assertEqual( doc.tag, "build" ) # root
		self.assertNotEquals( doc.find( e ), None )
		self.assertNotEquals( doc.find( "{0}/description".format( e ) ), None )
		self.assertNotEquals( doc.find( "{0}/traceback".format( e ) ), None )

		self.assertTrue( "self.runSetups()" in doc.find( "{0}/traceback".format( e ) ).text )

		if etree.__name__ == "lxml.etree":
			self.assertNotEquals( doc.find( '{0}[@returncode="{1}"]'.format( e, MomError.getReturnCode() ) )
								, None, "Wrong returncode in exception" )

	def testXmlReportOnException1( self ):
		# Covers runPreflightChecks phase

		def runPreFlightChecks_new():
			raise ConfigurationError( "Test Error" )

		# inject erroneous method
		self.build.runPreFlightChecks = runPreFlightChecks_new

		self._build()
		doc = etree.XML( self.getXmlReport().getReport() )

		e = self.EXCEPTION_LOCATION
		self.assertEqual( doc.tag, "build" ) # root
		self.assertNotEquals( doc.find( e ), None )
		self.assertNotEquals( doc.find( "{0}/description".format( e ) ), None )
		self.assertNotEquals( doc.find( "{0}/traceback".format( e ) ), None )

		self.assertTrue( "self.runPreFlightChecks()" in doc.find( "{0}/traceback".format( e ) ).text )

		if etree.__name__ == "lxml.etree":
			self.assertNotEquals( doc.find( '{0}[@returncode="{1}"]'.format( e, ConfigurationError.getReturnCode() ) )
								, None, "Wrong returncode in exception" )

	def testXmlReportOnException2( self ):
		# Covers run phase

		def runExecute_new():
			raise BuildError( "Test Error" )

		# inject erroneous method
		self.build.runExecute = runExecute_new

		self._build()
		doc = etree.XML( self.getXmlReport().getReport() )

		# only minor checks, rest already covered in previous tests
		e = self.EXCEPTION_LOCATION
		self.assertEqual( doc.tag, "build" ) # root
		self.assertNotEquals( doc.find( e ), None )

		self.assertTrue( "self.runExecute()" in doc.find( "{0}/traceback".format( e ) ).text )

	def testXmlReportOnExceptionInXmlReportGeneration( self ):
		def command_new( arg1, arg2 ):
			raise MomError( "Test Error" )

		# inject invalid XML template function into plugin
		logger = ConsoleLogger()
		self.build.addPlugin( logger )
		logger.getXmlTemplate = command_new

		self._build()

		converter = XmlReportConverter( self.getXmlReport() )
		text = converter.convertToText()
		self.assertTrue( "ConsoleLogger" in text )
		self.assertTrue( "Exception" in text )

if __name__ == "__main__":
	unittest.main()
