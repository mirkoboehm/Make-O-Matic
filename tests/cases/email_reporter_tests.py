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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from core.Exceptions import ConfigurationError, MomError, BuildError
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.plugins.reporters.EmailReporter import EmailReporter
from email.feedparser import FeedParser
from tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase
import email
import unittest

class EmailReporterTest( MomBuildMockupTestCase ):

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self, useScm = True )

		mApp().getSettings().set( Settings.EmailReporterDefaultRecipients, ["DR"] )
		mApp().getSettings().set( Settings.EmailReporterConfigurationErrorRecipients, ["CER"] )
		mApp().getSettings().set( Settings.EmailReporterMomErrorRecipients, ["MER"] )
		mApp().getSettings().set( Settings.EmailReporterSender, "S" )

		# add EmailReporter plugin
		self.reporter = EmailReporter( "TestEmailReporter" )
		self.build.addPlugin( self.reporter )

	def testCreateEmailOnNormalExit( self ):
		self.build.registerReturnCode( 0 ) # no failure
		self.build.runPreFlightChecks()
		email = self.reporter.createEmail()

		self.assertEquals( email.getToAddresses(), ["DR"] )

	def testCreateEmailOnConfiguratioError( self ):
		self.build.registerReturnCode( ConfigurationError.getReturnCode() )
		self.build.runPreFlightChecks()
		email = self.reporter.createEmail()

		self.assertTrue( "DR" in email.getToAddresses() )
		self.assertTrue( "CER" in email.getToAddresses() )

	def testCreateEmailOnMomError( self ):
		self.build.registerReturnCode( MomError.getReturnCode() )
		self.build.runPreFlightChecks()
		email = self.reporter.createEmail()

		self.assertTrue( "DR" in email.getToAddresses() )
		self.assertTrue( "MER" in email.getToAddresses() )

	def testCreateEmailOnBuildError1( self ):
		self.build.registerReturnCode( BuildError.getReturnCode() )
		scm = self.build.getProject().getScm()

		# commit1
		scm.setRevision( "409ae013ff1a9dccf41a60b4cefcd849309893bd" ) # commit by Mirko
		self.build.runPreFlightChecks()
		email = self.reporter.createEmail()
		self.assertTrue( "DR" in email.getToAddresses() )
		self.assertTrue( "mirko@kdab.com" in email.getToAddresses() )

	def testCreateEmailOnBuildError2( self ):
		self.build.registerReturnCode( BuildError.getReturnCode() )
		scm = self.build.getProject().getScm()

		# commit2
		scm.setRevision( "040acdfb5331caab182a072f8d68dec3f4a402e9" ) # commit by Kevin
		self.build.runPreFlightChecks()
		email = self.reporter.createEmail()
		self.assertTrue( "DR" in email.getToAddresses() )
		self.assertTrue( "krf@electrostorm.net" in email.getToAddresses() )

	def testCreateEmailNoRecipients( self ):
		mApp().getSettings().set( Settings.EmailReporterDefaultRecipients, None )
		self.build.runPreFlightChecks()
		email = self.reporter.createEmail()

		self.assertEquals( len( email.getToAddresses() ), 0 )

	def testCreateEmailSubjectWithValidRevision( self ):
		scm = self.build.getProject().getScm()

		scm.setRevision( "040acdfb5331caab182a072f8d68dec3f4a402e9" )
		self.build.runPreFlightChecks()

		email = self.reporter.createEmail()
		self.assertTrue( scm.getRevision()[:7] in email.getSubject(), "No abbreviated commit hash in subject" )

	def testCreateEmailSubjectWithInvalidRevision( self ):
		scm = self.build.getProject().getScm()

		scm.setRevision( "---" )
		self.build.runPreFlightChecks()

		email = self.reporter.createEmail()
		self.assertTrue( "N/A" in email.getSubject() )

	def testCreateEmailHtmlSummary( self ):
		scm = self.build.getProject().getScm()

		# set revision explicitly (with multi-line message)
		scm.setRevision( "35fe6206bf1c1b576c69e4001d345404cdfd41be" )
		self.build.runPreFlightChecks()

		text = self.reporter.createEmail().getMessageText( "DR" )

		msg = email.message_from_string( text )
		for part in msg.walk():
			contentType = part.get_content_type()
			if not contentType in ["text/plain", "text/html"]:
				continue

			payload = part.get_payload( decode = True )

			# simple test here. makes more sense to do manual tests with this
			self.assertTrue( "XmlReportTestBuild" in payload )
			self.assertTrue( "convenience" in payload ) # from commit message

if __name__ == "__main__":
	unittest.main()
