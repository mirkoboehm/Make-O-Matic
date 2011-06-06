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

import os
from core.Build import Build
from core.MApplication import MApplication
from datetime import datetime
import unittest
from core.helpers.RunCommand import RunCommand

class MomTestCase( unittest.TestCase ):
	'''MomTestCase is a base test case class that sets up and tears down the Build object.

	\note Tests do not load user configured settings!
	You may enable this by setting the environment variable MOM_TESTS_RUNNING to 0 '''

	ENV_KEY = "MOM_TESTS_RUNNING"

	MY_FILE_PATH = os.path.realpath( __file__ )
	MY_DIRECTORY = os.path.split( MY_FILE_PATH )[0]
	TEST_MOM_ENVIRONMENTS = os.path.abspath( os.path.join( MY_DIRECTORY , '..', 'cases', 'test-mom-environments' ) )
	TEST_DATA_DIRECTORY = os.path.abspath( os.path.join( MY_DIRECTORY , '..', 'data' ) )

	def __init__( self, methodName = 'runTest' ):
		unittest.TestCase.__init__( self, methodName )

		if not os.getenv( self.ENV_KEY ):
			os.environ[ self.ENV_KEY ] = "1"

	def setUp( self, createBuild = True ):
		self.startTime = datetime.utcnow()

		if MApplication.instance:
			# do not try this at home!
			MApplication.instance = None
		if createBuild:
			self.build = Build( name = "TestBuild" )

	def tearDown( self ):
		MApplication.instance = None

		#print( "[time: {0}]".format( datetime.utcnow() - self.startTime ) )

	def runCommand( self, cmd, description, timeout = None, zeroReturnCode = True ):
		'''Helper method to run shell commands in tests. It creates a RunCommand object, runs it, 
		and returns it. If the return code is not zero, it dumps the output of the command.'''
		runner = RunCommand( cmd, timeout )
		runner.run()
		if zeroReturnCode and runner.getReturnCode() != 0:
			print( '\n' )
			print( 'command failed: {0}'.format( description ) )
			print( 'output:' )
			print( runner.getStdOutAsString() )
			print( 'error output:' )
			print( runner.getStdErrAsString() )
		self.assertEqual( runner.getReturnCode() == 0, zeroReturnCode )
		return runner

