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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from core.helpers.Emailer import Email, Emailer
from tests.helpers.MomTestCase import MomTestCase
import unittest
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings

class EmailerTest( MomTestCase ):
	'''This test is not part of the test suite, because it will only succeed if an email server is configured properly.'''

	def testSendEmail( self ):
		mApp().getSettings().set( Settings.EmailerSmtpServer, 'mail.kdab.com' )
		email = Email()
		email.setFromAddress( 'mirko@kdab.com' )
		email.setToAddresses( 'mirko@kdab.com' )
		email.setSubject( 'Build report for {0}, revision {1}'.format( '<Project>', '<4711>' ) )
		email.addTextPart( '''\
This is a test email sent by make-o-matic.
Check it out at http://gitorious.org/make-o-matic
''' )
		email.addHtmlPart( """\
		<html>
			<head>make-o-matic Test Email</head>
			<body>
				<p>This is the HTML part of the test email<br>
					 Check out make-o-matic at <a href="http://gitorious.org/make-o-matic">Gitorious</a>.
				</p>
			</body>
		</html>
		""" )
		e = Emailer( 'Emailer' )
		try:
			e.setup()
			e.send( email )
			e.quit()
		except Exception as e:
			self.fail( 'Sending a test email failed: {0}'.format( e ) )


if __name__ == "__main__":
	unittest.main()
