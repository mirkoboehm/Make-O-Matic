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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import unittest
from core.plugins.reporters.EmailReporter import EmailReporter
from tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
from core.Exceptions import ConfigurationError, MomError, BuildError

class EmailReporterTest( MomBuildMockupTestCase ):

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self, useScm = True )

		mApp().getSettings().set( Settings.EmailReporterDefaultRecipients, ["DR"] )
		mApp().getSettings().set( Settings.EmailReporterConfigurationErrorRecipients, ["CER"] )
		mApp().getSettings().set( Settings.EmailReporterMomErrorRecipients, ["MER"] )
		mApp().getSettings().set( Settings.EmailReporterSender, ["S"] )

		# add EmailReporter plugin
		self.reporter = EmailReporter( "TestEmailReporter" )
		self.build.addPlugin( self.reporter )
		self.build.runPreFlightChecks()

	def testCreateEmail1( self ):
		self.build.registerReturnCode( 0 ) # no failure
		email = self.reporter.createEmail()

		self.assertEquals( email.getToAddresses(), ["DR"] )

	def testCreateEmail2( self ):
		self.build.registerReturnCode( ConfigurationError.getReturnCode() )
		email = self.reporter.createEmail()

		self.assertTrue( "DR" in email.getToAddresses() and "CER" in email.getToAddresses() )

	def testCreateEmail3( self ):
		self.build.registerReturnCode( MomError.getReturnCode() )
		email = self.reporter.createEmail()

		self.assertTrue( "DR" in email.getToAddresses() and "MER" in email.getToAddresses() )

	def testCreateEmail4( self ):
		self.build.registerReturnCode( BuildError.getReturnCode() )
		scm = self.build.getProject().getScm()

		# commit1
		scm.setRevision( "409ae013ff1a9dccf41a60b4cefcd849309893bd" ) # commit by Mirko
		self.build.runPreFlightChecks()
		email = self.reporter.createEmail()
		self.assertTrue( "DR" in email.getToAddresses() and "mirko@kdab.com" in email.getToAddresses() )

		# commit2
		scm.setRevision( "040acdfb5331caab182a072f8d68dec3f4a402e9" ) # commit by Kevin
		self.build.runPreFlightChecks()
		email = self.reporter.createEmail()
		self.assertTrue( "DR" in email.getToAddresses() and "krf@electrostorm.net" in email.getToAddresses() )

	def testCreateEmailNoRecipients( self ):
		mApp().getSettings().set( Settings.EmailReporterDefaultRecipients, None )
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
		self.failUnlessRaises( ConfigurationError, self.build.runPreFlightChecks )

		email = self.reporter.createEmail()
		self.assertTrue( "N/A" in email.getSubject() )

	# TODO: Implement at some point
	#def testCreateEmailBody( self ):

if __name__ == "__main__":
	unittest.main()
