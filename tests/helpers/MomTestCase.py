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

import unittest
from core.MApplication import MApplication
from core.Build import Build
from core.helpers.RunCommand import RunCommand

class MomTestCase( unittest.TestCase ):
	'''MomTestCase is a base test case class that sets up and tears down the Build object.'''

	def setUp( self ):
		if MApplication._instance:
			# do not try this at home!
			MApplication._instance = None
		self.build = Build()

	def tearDown( self ):
		MApplication._instance = None

	def runCommand( self, cmd, description ):
		'''Helper method to run shell commands in tests. It creates a RunCommand object, runs it, 
		and returns it. If the return code is not zero, it dumps the output of the command.'''
		runner = RunCommand( cmd )
		runner.run()
		if runner.getReturnCode() != 0:
			print( '\n' )
			print( 'command failed: {0}'.format( description ) )
			print( 'output:' )
			print( runner.getStdOut().decode() )
			print( 'error output:' )
			print( runner.getStdErr().decode() )
		return runner

