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

from core.plugins.reporters.Reporter import Reporter
from core.plugins.reporters.XmlReport import XmlReport
from core.helpers.GlobalMApp import mApp
from core.helpers.Emailer import Email, Emailer
from core.helpers.XmlReportConverter import XmlReportConverter
from core.Build import Build
from core.Settings import Settings
from core.Exceptions import MomError, BuildError, ConfigurationError
from core.plugins.sourcecode.RevisionInfo import RevisionInfo

class EmailReporter( Reporter ):

	def __init__( self, name = None ):
		Reporter.__init__( self, name )

		self.__info = None

	def preFlightCheck( self ):
		self.__info = None

		# try to get info, may fail
		self.__info = mApp().getProject().getScm().getRevisionInfo()

	def shutDown( self ):
		email = self.createEmail()

		if len( email.getToAddresses() ) == 0:
			mApp().debug( self, 'Not sending mail, no recipients added' )
			return

		# send mail
		e = Emailer()
		try:
			e.setup()
			e.send( email )
			e.quit()
			mApp().debug( self, 'Sent E-Mail to following recipients: {0}'.format( ", ".join( email.getToAddresses() ) ) )
		except Exception as e:
			mApp().debug( self, 'Sending E-Mail failed: {0}'.format( e ) )

	def createEmail( self ):
		instructions = mApp()
		assert isinstance( instructions, Build )

		# get settings
		reporterDefaultRecipients = mApp().getSettings().get( Settings.EmailReporterDefaultRecipients, False )
		reporterConfigurationErrorRecipients = mApp().getSettings().get( Settings.EmailReporterConfigurationErrorRecipients, False )
		reporterMomErrorRecipients = mApp().getSettings().get( Settings.EmailReporterMomErrorRecipients, False )
		reporterSender = mApp().getSettings().get( Settings.EmailReporterSender )
		reporterEnableHtml = mApp().getSettings().get( Settings.EmailReporterEnableHtml )

		# get revision info, do not crash here
		info = self.__info or RevisionInfo()
		revision = ( info.shortRevision if info.shortRevision else info.revision ) or "N/A"

		returnCode = instructions.getReturnCode()
		status = ( u"\u263A" if returnCode == 0 else u"\u2620" ).encode( "utf8" ) # to smile or not to smile, that's the question
		type = instructions.getSettings().get( Settings.ProjectBuildType )

		email = Email()

		# build header
		email.setSubject( '{0} {1} ({2}), {3}'.format( status, instructions.getName(), type, revision, ) )
		email.setFromAddress( reporterSender )

		# add recipients
		if reporterDefaultRecipients:
			email.setToAddresses( reporterDefaultRecipients )


		if returnCode == ConfigurationError.getReturnCode() or ( info.revision is None ):
			if reporterConfigurationErrorRecipients:
				email.addToAddresses( reporterConfigurationErrorRecipients )

		elif returnCode == BuildError.getReturnCode():
			if mApp().getSettings().get( Settings.EmailReporterNotifyCommitterOnFailure ):
				email.addToAddresses( [ info.committerEmail] )

		elif returnCode == MomError.getReturnCode():
			if reporterMomErrorRecipients:
				email.addToAddresses( reporterMomErrorRecipients )

		# body
		report = XmlReport( instructions )
		report.prepare()
		converter = XmlReportConverter( report )
		if reporterEnableHtml:
			email.addHtmlPart( converter.convertToHtml() )
		else:
			email.addTextPart( converter.convertToText( short = True ) )

		exception = mApp().getException()
		if exception:
			email.addTextAttachment( "{0}\n\n{1}".format( exception[0], exception[1] ), "build.log" )

		return email
