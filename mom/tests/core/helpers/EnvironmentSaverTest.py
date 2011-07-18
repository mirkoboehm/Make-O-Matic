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

from core.helpers.EnvironmentSaver import EnvironmentSaver
from mom.tests.helpers.MomTestCase import MomTestCase
import os
import unittest

class EnvironmentSaverTest( MomTestCase ):

	def testSetVariable( self ):
		testVariable = 'TEST_ENVIRONMENT_VARIABLE'
		testContent = 'TEST_CONTENT'
		with EnvironmentSaver():
			os.environ[testVariable] = testContent
			self.assertEqual( os.environ[ testVariable], testContent )
		self.assertTrue( testVariable not in os.environ )

	def testChangeDirectory( self ):
		oldCwd = os.getcwd()
		homeDir = os.path.expanduser( '~' )
		with EnvironmentSaver():
			os.chdir( homeDir )
			self.assertEqual( os.getcwd(), homeDir )
		self.assertEqual( os.getcwd(), oldCwd )

if __name__ == "__main__":
	unittest.main()
