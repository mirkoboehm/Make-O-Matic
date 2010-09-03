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

from core.modules.Reporter import Reporter
from core.modules.reporters.XmlReport import XmlReport
from core.helpers.GlobalMApp import mApp
from core.helpers.Emailer import Email, Emailer
from core.helpers.XmlReportConverter import XmlReportConverter

class EmailReporter( Reporter ):

	def __init__( self, name = None ):
		Reporter.__init__( self, name )

	def wrapUp( self ):
		report = XmlReport( mApp() )
		report.prepare()
		xml = report.getReport()

		conv = XmlReportConverter( xml )
		html = conv.convertToHtml()

		email = Email()
		email.setSubject( 'Build report for {0}, revision {1}'.format( '<Project>', '<4711>' ) )
		email.addHtmlPart( html )
		# TODO: Add recipients list

		#print( "DEBUG: " + html )

		e = Emailer( 'Emailer' )
		try:
			e.setup()
			e.send( email )
			e.quit()
		except Exception as e:
			mApp().debug( self, 'Sending a test email failed: {0}'.format( e ) )

