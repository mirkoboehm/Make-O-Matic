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
import os
import sys
from core.Settings import Settings
from core.helpers.RunCommand import RunCommand
from core.helpers.GlobalMApp import mApp
from tests.helpers.MomTestCase import MomTestCase

class SimpleProjectTests( MomTestCase ):
	'''SimpleProjectTests runs the simple_project_run test build script in the three major run modes.
	It assumes that it is executed in the tests/ sub-directory of the mom repository.'''

	BuildScriptName = os.path.join( 'basic', 'simple_project_run.py' )

	def _querySetting( self, name ):
		cmd = '{0} {1} query {2}'.format( sys.executable, SimpleProjectTests.BuildScriptName, name )
		runner = RunCommand( cmd )
		runner.run()
		return runner

	def testQueryProjectName( self ):
		runner = self._querySetting( Settings.ProjectName )
		self.assertEquals( runner.getReturnCode(), 0 )
		line = runner.getStdOut().decode().strip()
		self.assertEquals( line, 'project.name: Simple Project Run Test' )

	def testQueryMomVersion( self ):
		runner = self._querySetting( Settings.MomVersionNumber )
		self.assertEquals( runner.getReturnCode(), 0 )
		line = runner.getStdOut().decode().strip()
		expectedVersion = mApp().getSettings().get( Settings.MomVersionNumber )
		self.assertEquals( line, '{0}: {1}'.format( Settings.MomVersionNumber, expectedVersion ) )

	def testPrintCurrentRevision( self ):
		cmd = '{0} {1} print current-revision'.format( sys.executable, SimpleProjectTests.BuildScriptName )
		runner = RunCommand( cmd )
		runner.run()
		self.assertEquals( runner.getReturnCode(), 0 )
		line = runner.getStdOut().decode().strip()
		# we cannot know what the current revision is, but if the return code is not zero, it should not be empty:
		self.assertTrue( line )

	def _testBuild( self, buildType ):
		cmd = '{0} {1} -v -t {2}'.format( sys.executable, SimpleProjectTests.BuildScriptName, buildType )
		runner = RunCommand( cmd )
		runner.run()
		if runner.getReturnCode() != 0:
			print( '\nbuild script run failed for build type {0}'.format( buildType ) )
			print( 'output:' )
			print( runner.getStdOut().decode() )
			print( 'error output:' )
			print( runner.getStdErr().decode() )
		return runner

	def testEBuild( self ):
		runner = self._testBuild( 'E' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testMBuild( self ):
		runner = self._testBuild( 'M' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testCBuild( self ):
		runner = self._testBuild( 'C' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testDBuild( self ):
		runner = self._testBuild( 'D' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testSBuild( self ):
		runner = self._testBuild( 'S' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testHBuild( self ):
		runner = self._testBuild( 'H' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testPBuild( self ):
		runner = self._testBuild( 'P' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testFBuild( self ):
		runner = self._testBuild( 'F' )
		self.assertEquals( runner.getReturnCode(), 0 )

if __name__ == "__main__":
	unittest.main()
