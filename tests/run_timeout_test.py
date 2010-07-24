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

from core.Project import Project
from core.helpers.RunCommand import RunCommand
import unittest

class RunWithTimeoutTest( unittest.TestCase ):

	def testRunWithTimeout( self ):
		project = Project( "Simple Project Run Test", "0.5.0" )
		timeout = 5
		command = 'sleep 10'
		runner = RunCommand( project, command, timeout, True )
		runner.run()
		self.assertTrue( runner.getTimedOut() )
		self.assertTrue( runner.getReturnCode() != 0 )

	def testRunWithoutTimeout( self ):
		project = Project( "Simple Project Run Test", "0.5.0" )
		timeout = 10
		command = 'sleep 5'
		runner = RunCommand( project, command, timeout, True )
		runner.run()
		self.assertFalse( runner.getTimedOut() )
		self.assertTrue( runner.getReturnCode() == 0 )

if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
