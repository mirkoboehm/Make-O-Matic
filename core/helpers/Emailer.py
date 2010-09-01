# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
# 
# make-o-matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# make-o-matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <http://www.gnu.org/licenses/>.
from core.MObject import MObject
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP, SMTPHeloError, SMTPAuthenticationError, SMTPException
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.Exceptions import ConfigurationError

class Email( MObject ):
	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.__msg = MIMEMultipart( 'alternative' )

	def _getMessage( self ):
		return self.__msg

	def setFromAddress( self, address ):
		self._getMessage()[ 'From' ] = address

	def getFromAddress( self ):
		return self._getMessage()[ 'From' ]

	def setToAddresses( self, addresses ):
		self._getMessage()[ 'To' ] = addresses

	def getToAddresses( self ):
		return self._getMessage()[ 'To' ]

	def setSubject( self, subject ):
		self._getMessage()['Subject'] = subject

	def getSubject( self ):
		return self._getMessage()['Subject']

	def addTextPart( self, text ):
		self._getMessage().attach( MIMEText( text, 'plain' ) )

	def addHtmlPart( self, html ):
		self._getMessage().attach( MIMEText( html, 'html' ) )

	def getMessageText( self ):
		return self._getMessage().as_string()

class Emailer( MObject ):
	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.__server = None

	def setup( self ):
		server = mApp().getSettings().get( Settings.EmailerSmtpServer, False )
		if not server:
			raise ConfigurationError( 'No emailer SMTP server specified, please check configuration!' )
		self.__server = SMTP( server )
		if mApp().getSettings().get( Settings.EmailerDoLogin, False ):
			user = mApp().getSettings().get( Settings.EmailerUsername )
			password = mApp().getSettings().get( Settings.EmailerPassword )
			try:
				self.__server.login( user, password )
			except SMTPHeloError as e:
				raise ConfigurationError( 'The SMTP server rejected the connection: {0}'.format( e ) )
			except SMTPAuthenticationError:
				raise ConfigurationError( 'Emailer error, login failed: {0}'.format( e ) )
			except SMTPException as e:
				raise ConfigurationError( 'Emailer error, no suitable authentication method was found: {0}'.format( e ) )
		if mApp().getSettings().get( Settings.EmailerUseTls, False ):
			self.__server.starttls()
			self.__server.ehlo()

	def send( self, email ):
		self.__server.sendmail( email.getFromAddress(), email.getToAddresses(), email.getMessageText() )

	def quit( self ):
		self.__server.quit()

