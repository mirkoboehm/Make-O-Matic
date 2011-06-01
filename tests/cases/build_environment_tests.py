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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os, unittest
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.environments.Environments import Environments
from core.loggers.ConsoleLogger import ConsoleLogger
from core.environments.Dependency import Dependency
from core.helpers.EnvironmentSaver import EnvironmentSaver
from tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase

class BuildEnvironmentTests( MomBuildMockupTestCase ):

	MY_FILE_PATH = os.path.realpath( __file__ )
	MY_DIRECTORY = os.path.split( MY_FILE_PATH )[0]
	TEST_MOM_ENVIRONMENTS = os.path.join( MY_DIRECTORY , 'test-mom-environments' )

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self, useEnvironments = True )

		mApp().getSettings().set( Settings.ScriptLogLevel, 1 )
		mApp().getSettings().set( Settings.EnvironmentsBaseDir, self.TEST_MOM_ENVIRONMENTS )
		mApp().addLogger( ConsoleLogger() )

	def _printMatches( self, matches ):
		return # disabled
		for match in matches:
			print( match.makeDescription() )

	def testTryFindNonExistantEnv( self ):
		dep = [ 'nonsense-1.0.0' ]
		environments = Environments( dep )
		matches = environments.findMatchingEnvironments()
		self.assertEquals( len( matches ), 0 )

	def testTryFindSingleEnv( self ):
		dep = [ 'dep-a-1.0.0' ]
		environments = Environments( dep )
		matches = environments.findMatchingEnvironments()
		self.assertEquals( len( matches ), 1 )
		for match in matches: # there is only one :-)
			self.assertEquals( match.makeDescription(), 'dep-a-1.0.0' )

	def testTryFindThreeMatches( self ):
		dep = [ 'dep-a-1.?.0' ]
		environments = Environments( dep )
		matches = environments.findMatchingEnvironments()
		# there should be 3 matches
		self.assertEquals( len( matches ), 3 )
		# check if every environment contains every dependency only once
		allPaths = []
		for environment in matches:
			paths = []
			for dependency in environment.getDependencies():
				self.assertTrue( dependency.getFolder() not in paths )
				# this must be true because there is only one dependency we are looking for, so every path should appear only once
				self.assertTrue( dependency.getFolder() not in allPaths )
				self.assertTrue( os.path.isdir( dependency.getFolder() ) )
				paths.append( dependency.getFolder() )
				allPaths.append( dependency.getFolder() )

	def testApplyPackageConfiguration( self ):
		packageFolder = os.path.join( self.TEST_MOM_ENVIRONMENTS, 'dep-a-1.1.0' )
		packageFile = os.path.join( packageFolder, Dependency._ControlFileName )
		self.assertTrue( os.path.exists( packageFile ) )
		dep = Dependency()
		dep.setFolder( packageFolder )
		self.assertTrue( dep._readControlFile( packageFile ) )
		self.assertTrue( dep.isEnabled() )
		self.assertEquals( dep.getObjectStatus(), 'test-dep-a-1.1.0' )
		with EnvironmentSaver():
			dep.apply()
			self.assertEquals( os.environ[ 'EXAMPLE_VARIABLE'], 'example_variable' )
			self.assertTrue( os.environ['PATH'].startswith( 'example_path' ) )

	def testApplyDisabledPackageConfiguration( self ):
		packageFolder = os.path.join( self.TEST_MOM_ENVIRONMENTS, 'dep-a-1.2.0' )
		packageFile = os.path.join( packageFolder, Dependency._ControlFileName )
		self.assertTrue( os.path.exists( packageFile ) )
		dep = Dependency()
		dep.setFolder( packageFolder )
		self.assertTrue( dep._readControlFile( packageFile ) )
		self.assertTrue( not dep.isEnabled() )
		self.assertEquals( dep.getObjectStatus(), 'test-disabled-dep-a-1.2.0' )
		self.assertEquals( dep.getScore(), 120 )

	def testTryFindTwoEnvironments( self ):
		dep = [ 'dep-a-1.0.0', 'dep-b-2.2.0' ]
		environments = Environments( dep )
		matches = environments.findMatchingEnvironments()
		self._printMatches( matches )
		self.assertEquals( len( matches ), 1 )

	def testTryFindTwoEnvironmentsSameFolder( self ):
		dep = [ 'dep-a-1.0.0', 'dep-b-2.0.0' ]
		environments = Environments( dep )
		matches = environments.findMatchingEnvironments()
		self._printMatches( matches )
		self.assertEquals( len( matches ), 1 )

	def testTryFindNEnv( self ):
		dep = [ 'dep-a-1.?.0', 'dep-b-2.?.0' ]
		environments = Environments( dep )
		matches = environments.findMatchingEnvironments()
		self._printMatches( matches )
		self.assertEquals( len( matches ), 7 )

if __name__ == "__main__":
	unittest.main()
