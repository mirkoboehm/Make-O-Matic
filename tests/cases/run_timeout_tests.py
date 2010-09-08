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

from core.helpers.RunCommand import RunCommand
import unittest
from core.MApplication import MApplication
from core.Build import Build
import sys

# FIXME the test will need a Build object now! setup/tearDown?
class RunWithTimeoutTest( unittest.TestCase ):

	def setUp( self ):
		if MApplication._instance:
			# do not try this at home!
			MApplication._instance = None
		self.build = Build()
		if sys.platform == 'win32':
			self.sleepCommand = [ 'ping', '127.0.0.1', '-n', '10' ]
		else:
			self.sleepCommand = [ 'sleep', '5']

	def tearDown( self ):
		MApplication._instance = None

	def testRunWithTimeout( self ):
		timeout = 1
		runner = RunCommand( self.sleepCommand, timeout, True )
		runner.run()
		self.assertTrue( runner.getTimedOut() )
		self.assertNotEquals( runner.getReturnCode(), 0 )

	def testRunWithoutTimeout( self ):
		timeout = 10
		runner = RunCommand( self.sleepCommand, timeout, True )
		runner.run()
		self.assertFalse( runner.getTimedOut() )
		self.assertEqual( runner.getReturnCode(), 0 )

if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
