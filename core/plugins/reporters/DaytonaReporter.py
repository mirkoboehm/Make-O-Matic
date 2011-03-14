# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2011 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Frank Osterfeld <frank.osterfeld@kdab.com>
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
from core.helpers.XmlReport import XmlReport
from core.helpers.GlobalMApp import mApp
from core.helpers.XmlReportConverter import XmlReportConverter
from core.Build import Build
from core.Settings import Settings
from core.Exceptions import MomError, BuildError, ConfigurationError
from core.helpers.TypeCheckers import check_for_list_of_strings_or_none, check_for_string

import json
import urllib2

def sendMessage( msg, url ):
	msg = json.dumps( msg )
	opener = urllib2.build_opener( urllib2.HTTPHandler )
	request = urllib2.Request( url, data=msg )
	request.get_method = lambda: 'PUT'
	req_url = opener.open( request )

class DaytonaReporter( Reporter ):
	"""
	This plugin enables reporting build reports to a Daytona Bot specified in the settings.
	
	Available settings:
	* DaytonaPostUrl (*)
		  o The URL of the daytona bot, e.g. http://somehost:8080/daytona/notify?format=json
		  
	@note Settings marked with a (*) are required
	"""

	PostUrlKey = "daytonareporter.posturl"

	def preFlightCheck( self ):
		# check settings, may fail
		settings = mApp().getSettings()
		check_for_string( settings.get( DaytonaReporter.PostUrlKey ), "DaytonaPostUrl Must be a valid URL" )
	
	def shutDown( self ):
		msg = self._createMessage()

		# send message
		try:
			# get settings
			# reporterSender = mApp().getSettings().get( Settings.EmailReporterSender )
			postUrl = mApp().getSettings().get( DaytonaReporter.PostUrlKey )
			sendMessage( msg, postUrl )
			mApp().debug( self, 'Sent message to daytona bot at {0}'.format( postUrl ) )
		except Exception as e:
			mApp().debug( self, 'Sending to Daytona bot failed: {0}'.format( e ) )

	def getObjectStatus( self ):
			return ""

	def _createMessage( self ):
		instructions = mApp()
		assert isinstance( instructions, Build )

		msg = {}

		# get revision info, do not crash here
		info = instructions.getProject().getScm().getRevisionInfo()
		revision = ( info.shortRevision if info.shortRevision else info.revision ) or "N/A"

		returnCode = instructions.getReturnCode()
		status = ( "☺" if returnCode == 0 else "☠" ) # to smile or not to smile, that's the question
		type = mApp().getSettings().get( Settings.ProjectBuildType )

		# build header
		text = '{0} {1} ({2}), {3}, {4} by {5}'.format( 
				status,
				instructions.getName(),
				type,
				instructions.getSystemShortName(),
				revision,
				info.committerName
				)
		
		msg["text"] = text
		msg["MOM-Build-Name"] = mApp().getName()
		msg["MOM-Version"] = mApp().getMomVersion()
		msg["MOM-Success"] = "true" if returnCode == 0 else "false" 
		msg["MOM-Project"] = instructions.getName()
		msg["sender"] = "make-o-matic"

		return msg
