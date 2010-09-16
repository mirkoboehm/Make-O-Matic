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

import unittest
from core.Build import Build
import sys
from tests.helpers.MomTestCase import MomTestCase

class RunWithTimeoutTest( MomTestCase ):

	def setUp( self ):
		MomTestCase.setUp( self, False )
		self.build = Build()
		if sys.platform == 'win32':
			self.sleepCommand = [ 'ping', '127.0.0.1', '-n', '2' ]
		else:
			self.sleepCommand = [ 'sleep', '2']

	def testRunWithTimeout( self ):
		timeout = 1
		runner = self.runCommand( self.sleepCommand, self.sleepCommand[0], timeout, False )
		self.assertTrue( runner.getTimedOut() )

	def testRunWithoutTimeout( self ):
		timeout = 10
		runner = self.runCommand( self.sleepCommand, self.sleepCommand[0], timeout, True )
		self.assertFalse( runner.getTimedOut() )

if __name__ == "__main__":
	unittest.main()
