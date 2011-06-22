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
from core.Plugin import Plugin
from core.Settings import Settings
from core.helpers.Emailer import Email, Emailer
from core.helpers.GlobalMApp import mApp
from core.helpers.TemplateSupport import MomTemplate
from core.helpers.TypeCheckers import check_for_list_of_strings_or_none, check_for_string
from core.helpers.XmlReport import InstructionsXmlReport
from core.helpers.XmlReportConverter import XmlReportConverter
import os.path
from core.helpers.RevisionInfo import RevisionInfo


class EmailReporter( Plugin ):
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

	def notify( self ):
		email = self.createEmail()

		if len( email.getToAddresses() ) == 0:
			mApp().debug( self, 'Not sending mail, no recipients added' )
			return

		# send mail
		e = Emailer()
		e.setup()
		e.send( email )
		e.quit()
		mApp().debug( self, 'Sent E-Mail to following recipients: {0}'.format( ", ".join( email.getToAddresses() ) ) )

	def getObjectStatus( self ):
		if not XmlReportConverter.hasXsltSupport():
			return "Cannot generate HTML, probably due to missing python-lxml package"
		else:
			return ""

	def createHtmlSummary( self ):
		SUMMARY_TEMPLATE_PATH = os.path.join( self._PLUGIN_DATA_DIR, "EmailReporter_SummaryTemplate.html" )

		instructions = mApp()
		assert isinstance( instructions, Build )
		info = instructions.getProject().getScm().getRevisionInfo()

		d = dict()
		returnCode = instructions.getReturnCode()
		d["my.returncode"] = returnCode
		d["my.statusIcon"] = ( "☺" if returnCode == 0 else "☠" )
		d["my.statusSummary"] = ( "success" if returnCode == 0 else "ERROR" )
		d["my.statusDetails"] = "Failed steps: ".format( " ".join( instructions.getFailedSteps() ) ) \
				if len( instructions.getFailedSteps() ) > 0 else "---"
		d["my.bgcolor"] = ( "#00FF33" if returnCode == 0 else "red" )
		d["my.scmCommitterName"] = info.committerName or ""
		d["my.scmCommitTime"] = info.commitTimeReadable or ""
		d["my.scmCommitMessage"] = info.commitMessage or ""
		d["my.footer"] = "Build took: {0}".format( instructions.getTimeKeeper().deltaString() )

		templateString = open( SUMMARY_TEMPLATE_PATH, 'r' ).read()
		s = MomTemplate( templateString )
		s.overwrites = d
		htmlString = s.substitute()
		return htmlString

	def createHtmlSummaryNG( self ):
		report = InstructionsXmlReport( mApp() )
		conv = XmlReportConverter( report )
		htmlString = conv.convertToHtml( summaryOnly = True )
		return htmlString

	def createEmail( self ):
		instructions = mApp()
		assert isinstance( instructions, Build )

		# get settings
		reporterDefaultRecipients = mApp().getSettings().get( Settings.EmailReporterDefaultRecipients, False )
		reporterConfigurationErrorRecipients = mApp().getSettings().get( Settings.EmailReporterConfigurationErrorRecipients, False )
		reporterMomErrorRecipients = mApp().getSettings().get( Settings.EmailReporterMomErrorRecipients, False )
		reporterSender = mApp().getSettings().get( Settings.EmailReporterSender )
		reporterUseCompression = mApp().getSettings().get( Settings.EmailReporterUseCompressionForAttachments, False )

		# get revision info, do not crash here
		try:
			info = instructions.getProject().getScm().getRevisionInfo()
		except MomError:
			info = RevisionInfo()
		revision = ( info.shortRevision if info.shortRevision else info.revision ) or "N/A"

		returnCode = instructions.getReturnCode()
		status = ( "☺" if returnCode == 0 else "☠" ) # to smile or not to smile, that's the question
		type = instructions.getSettings().get( Settings.ProjectBuildType )

		email = Email()

		# build header
		email.setSubject( '{0} {1} ({2}), {3}, {4}'.format( 
				status,
				instructions.getName(),
				type,
				instructions.getSystemShortName(),
				revision
				) )
		email.setFromAddress( reporterSender )

		# set custom headers
		email.setCustomHeader( "MOM-Build-Name", mApp().getName() )
		email.setCustomHeader( "MOM-Version", mApp().getMomVersion() )

		# add recipients
		if reporterDefaultRecipients:
			email.setToAddresses( reporterDefaultRecipients )

		if returnCode == ConfigurationError.getReturnCode() or ( info.revision is None ):
			if reporterConfigurationErrorRecipients:
				email.addToAddresses( reporterConfigurationErrorRecipients )

		elif returnCode == BuildError.getReturnCode():
			if mApp().getSettings().get( Settings.EmailReporterNotifyCommitterOnFailure ):
				if info.committerEmail:
					email.addToAddresses( [ info.committerEmail] )
				else:
					mApp().debug( self, 'Could not add committer {0} as recipient, email address is missing: {0}'
								.format( info.committerName ) )

		elif returnCode == MomError.getReturnCode():
			if reporterMomErrorRecipients:
				email.addToAddresses( reporterMomErrorRecipients )

		# body
		report = InstructionsXmlReport( instructions )
		converter = XmlReportConverter( report )

		### text and html part
		# summary
		email.attachAlternativeTextPart( 
				converter.convertToTextSummary(),
				self.createHtmlSummaryNG()
		)

		# body
		textReport = converter.convertToText( short = True )
		htmlReport = converter.convertToHtml()
		if htmlReport:
			email.attachAlternativeTextPart( textReport, htmlReport )
		else:
			email.attachTextPart( textReport )

		# attachments
		exception = mApp().getException()
		if exception:
			email.addTextAttachment( "{0}\n\n{1}".format( exception[0], exception[1] ), "build.log", useCompression = reporterUseCompression )
		elif returnCode != 0:
			email.addTextAttachment( converter.convertToFailedStepsLog(), "failed-steps.log", useCompression = reporterUseCompression )

		return email
