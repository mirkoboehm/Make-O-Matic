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

from __future__ import unicode_literals
from core.Build import Build
from core.Exceptions import MomError, BuildError, ConfigurationError
from core.Settings import Settings
from core.helpers.Emailer import Email, Emailer
from core.helpers.GlobalMApp import mApp
from core.helpers.RevisionInfo import RevisionInfo
from core.helpers.TypeCheckers import check_for_list_of_strings_or_none, check_for_string, check_for_list_of_strings
from core.helpers.XmlReport import InstructionsXmlReport
from core.helpers.XmlReportConverter import XmlReportConverter
from core.plugins.reporters.Reporter import Reporter


class EmailReporter( Reporter ):
	"""
	This plugin enables reporting build reports to a list of email recipients specified in the settings.
	EmailReporter allows you to specify multiple recipients list, which are notified on special cases.
	
	@warning Valid Emailer settings are required, see Emailer plugin for documentation
	
	Available settings:
	* EmailReporterEnableHtml
		  o This enables reporting in HTML instead of plain text
	* EmailReporterSender (*)
		  o This specifies the email address of the sender
	* EmailReporterDefaultRecipients
		  o This is a list of email addresses that get notified on every build (Example usage: Build report mailing list)
	* EmailReporterConfigurationErrorRecipients
		  o This is a list of email addresses that get notified when a build errors out with a ConfigurationError, e.g. "svn" not found in PATH
	* EmailReporterMomErrorRecipients
		  o This is a list of email addresses that get notified when a build errors out with a MomError, e.g. missing python packages
	* EmailReporterNotifyCommitterOnFailure
		  o This enables sending email reports to the committer who broke the last build. (Email is extracted from the VCS history)
		  
	@note Settings marked with a (*) are required
	"""

	def __init__( self, name = None ):
		super( EmailReporter, self ).__init__( name = name )

		self.setRecipients( [] )
		self.setEnableFullReport( False )

	def preFlightCheck( self ):
		# check settings, may fail
		settings = mApp().getSettings()
		for setting in [
					Settings.EmailReporterDefaultRecipients,
					Settings.EmailReporterConfigurationErrorRecipients,
					Settings.EmailReporterMomErrorRecipients
					]:
			value = settings.get( setting, False )
			check_for_list_of_strings_or_none( settings.get( setting, False ),
				"{0} must be a list of valid email addresses, not \"{1}\"".format( setting, value ) )

		check_for_string( settings.get( Settings.EmailReporterSender ), "EmailReporterSender must be a valid email address" )

	def createEmail( self ):
		email = Email()
		self._initEmailHeader( email )
		self._initEmailBody( email )
		self._initEmailRecipients( email )
		return email

	def setEnableFullReport( self, enable ):
		self.__enableFullReport = enable

	def getEnableFullReport( self ):
		return self.__enableFullReport

	def setRecipients( self, recipients ):
		"""If this is set, only these recipients will receive an email."""

		check_for_list_of_strings( recipients, "Please pass a valid list of recipients (strings)" )
		self.__recipientList = recipients

	def getRecipients( self ):
		return self.__recipientList

	def notify( self ):
		assert isinstance( mApp(), Build )

		email = self.createEmail()

		if len( email.getToAddresses() ) == 0:
			mApp().debug( self, 'Not sending mail, no recipients added' )
			return

		# send mail, this may throw an exception
		e = Emailer()
		e.setup()
		e.send( email )
		e.quit()
		mApp().debug( self, 'Sent E-Mail to following recipients: {0}'.format( ", ".join( email.getToAddresses() ) ) )
		self._setIsReportSent( True )

	def getObjectStatus( self ):
		if not XmlReportConverter.hasXsltSupport():
			return "Cannot generate HTML, probably due to missing python-lxml package"

		if len( self.getRecipients() ) > 0:
			typeString = "full report" if self.getEnableFullReport() else "summary"
			return "Recipients: {0} ({1})".format( ", ".join( self.__recipientList ), typeString )

		return "Recipients: (Using pre-configured settings)"

	def _getRevisionInfo( self ):
		# get revision info, do not crash here
		try:
			info = mApp().getProject().getScm().getRevisionInfo()
		except MomError:
			info = RevisionInfo()

		return info

	def getRecipientList( self ):
		# use overwrite if set
		if len( self.getRecipients() ) > 0:
			return self.getRecipients()

		info = self._getRevisionInfo()
		returnCode = mApp().getReturnCode()

		# get settings
		reporterDefaultRecipients = mApp().getSettings().get( Settings.EmailReporterDefaultRecipients, False )
		reporterConfigurationErrorRecipients = mApp().getSettings().get( Settings.EmailReporterConfigurationErrorRecipients, False )
		reporterMomErrorRecipients = mApp().getSettings().get( Settings.EmailReporterMomErrorRecipients, False )

		recipients = set()
		if reporterDefaultRecipients:
			recipients.update( reporterDefaultRecipients )

		if returnCode == ConfigurationError.getReturnCode() or ( info.revision is None ):
			if reporterConfigurationErrorRecipients:
				recipients.update( reporterConfigurationErrorRecipients )

		elif returnCode == BuildError.getReturnCode():
			if mApp().getSettings().get( Settings.EmailReporterNotifyCommitterOnFailure ):
				if info.committerEmail:
					recipients.add( info.committerEmail )
				else:
					mApp().debug( self, 'Could not add committer {0} as recipient, email address is missing: {0}'
								.format( info.committerName ) )

		elif returnCode == MomError.getReturnCode():
			if reporterMomErrorRecipients:
				recipients.update( reporterMomErrorRecipients )

		return recipients

	def _initEmailHeader( self, email ):
		reporterSender = mApp().getSettings().get( Settings.EmailReporterSender )

		info = self._getRevisionInfo()
		revision = ( info.shortRevision if info.shortRevision else info.revision ) or "N/A"

		returnCode = mApp().getReturnCode()
		status = ( "☺" if returnCode == 0 else "☠" ) # to smile or not to smile, that's the question
		type = mApp().getSettings().get( Settings.ProjectBuildType )

		# build header
		email.setSubject( '{0} {1} ({2}), {3}, {4}'.format( 
				status,
				mApp().getName(),
				type,
				mApp().getSystemShortName(),
				revision
				) )
		email.setFromAddress( reporterSender )

		# set custom headers
		email.setCustomHeader( "MOM-Build-Name", mApp().getName() )
		email.setCustomHeader( "MOM-Version", mApp().getMomVersion() )

		return email

	def _initEmailBody( self, email ):
		# body
		reporterUseCompression = mApp().getSettings().get( Settings.EmailReporterUseCompressionForAttachments, False )

		report = InstructionsXmlReport( mApp() )
		converter = XmlReportConverter( report )

		### text and html part
		# summary
		email.attachAlternativeTextPart( 
				converter.convertToTextSummary(),
				converter.convertToHtml( summaryOnly = True )
		)

		# report
		if self.getEnableFullReport():
			email.attachAlternativeTextPart( 
					converter.convertToText( short = True ),
					converter.convertToHtml()
			)

			returnCode = mApp().getReturnCode()
			if returnCode != 0:
				email.addTextAttachment( converter.convertToFailedStepsLog(), "failed-steps.log", useCompression = reporterUseCompression )

		# attachments
		exception = mApp().getException()
		if exception:
			traceback = u"\n".join( exception[1] )
			email.addTextAttachment( "{0}\n\n{1}".format( exception[0], traceback ), "exception.log", useCompression = reporterUseCompression )

		return email

	def _initEmailRecipients( self, email ):
		# add addresses
		recipients = self.getRecipientList()

		email.setToAddresses( recipients )
		return email
