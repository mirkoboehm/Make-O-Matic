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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
from tests.helpers.MomTestCase import MomTestCase
import os, inspect, unittest
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.environments.Environments import Environments
from test.test_iterlen import len
from core.loggers.ConsoleLogger import ConsoleLogger

class BuildEnvironmentTests( MomTestCase ):

	myFile = inspect.getfile( inspect.currentframe() )
	myFilePath = os.path.split( myFile )
	myDir = myFilePath[0]
	TestMomEnvironments = os.path.join( myDir, 'test-mom-environments' )

	def setUp( self ):
		MomTestCase.setUp( self )
		mApp().getSettings().set( Settings.ScriptLogLevel, 5 )
		mApp().getSettings().set( Settings.EnvironmentsBaseDir, BuildEnvironmentTests.TestMomEnvironments )
		mApp().addLogger( ConsoleLogger() )

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

	def testTryFindTwoMatches( self ):
		dep = [ 'dep-a-1.?.0' ]
		environments = Environments( dep )
		matches = environments.findMatchingEnvironments()
		environments.describe( '' )
		# check if every environment contains every dependency only once
		for environment in matches:
			paths = []
			for dependency in environment.getDependencies():
				self.assertTrue( dependency.getFolder() not in paths )
				self.assertTrue( os.path.isdir( dependency.getFolder() ) )
				paths.append( dependency.getFolder() )
		self.assertEquals( len( matches ), 1 )

if __name__ == "__main__":
	unittest.main()
