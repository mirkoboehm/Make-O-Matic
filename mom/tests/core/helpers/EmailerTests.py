# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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

from core.helpers.Emailer import Email, Emailer
from mom.tests.helpers.MomTestCase import MomTestCase
import unittest
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
import sys

class EmailerTests( MomTestCase ):
	'''This test is not part of the test suite, because it will only succeed if an email server is configured properly.'''

	def testSendEmail( self ):
		# force loading settings from configuration files
		mApp().getSettings().evalConfigurationFiles()

		email = Email()
		email.setToAddresses( ['kevin.funk@kdab.com'] )
		email.setFromAddress( mApp().getSettings().get( Settings.EmailReporterSender ) )

		email.setSubject( 'EmailerTest email' )

		email.attachAlternativeTextPart(
		'''\
		This is a test email sent by Make-O-Matic.
		Check it out at http://github.com/KDAB/Make-O-Matic
		''',
		"""\
		<html>
			<head>Make-O-Matic Test Email</head>
			<body>
				<p>This is the HTML part of the test email<br>
					 Check out Make-O-Matic at <a href="http://github.com/KDAB/Make-O-Matic">GitHub</a>.
				</p>
			</body>
		</html>
		""" )

		attachmentText = "TEST:\n" + "\n".join( sys.path )
		email.addTextAttachment( attachmentText, "testfile1.txt", False )
		email.addTextAttachment( attachmentText, "testfile2.txt", True )

		e = Emailer( 'Emailer' )
		e.setup()
		e.send( email )
		e.quit()

if __name__ == "__main__":
	unittest.main()
