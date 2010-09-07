# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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
from core.Project import Project
from core.Settings import Settings
from core.MApplication import MApplication
import os.path
import inspect
from core.environments.Environments import Environments
from core.modules.tools.cmake.CMakeBuilder import CMakeBuilder
from core.Configuration import Configuration
from core.modules.testers.CTest import CTest
from core.modules.packagers.CPack import CPack
from core.helpers.BoilerPlate import setupStandardBuild
import sys

class MomBuildMockupTestCase( unittest.TestCase ):
	'''MomTestCase is a base test case class that sets up and tears down the Build object.'''

	def setUp( self ):
		if MApplication._instance:
			# do not try this at home!
			MApplication._instance = None

		self._initializeBuildMockup()

	def _initializeBuildMockup( self ):
		myFile = inspect.getfile( inspect.currentframe() )
		myFilePath = os.path.split( myFile )
		myDir = myFilePath[0]
		testMomEnvironments = os.path.join( myDir, 'test-mom-environments' )
		sys.argv = [] # reset command line arguments

		self.build = setupStandardBuild( 'XmlReportTestBuild' )
		project = Project( 'XmlReportTestProject' )
		self.build.setProject( project )
		project.createScm( 'git:git@gitorious.org:make-o-matic/mom.git' )
		environments = Environments( [ 'Qt-4.[67].?-Shared-*' ], 'Qt 4', project )

		debug = Configuration( 'Debug', environments, )
		cmakeDebug = CMakeBuilder()
		debug.addPlugin( cmakeDebug )

		release = Configuration( 'Release', environments )
		cmakeRelease = CMakeBuilder()
		release.addPlugin( cmakeRelease )
		release.addPlugin( CTest() )
		release.addPlugin( CPack() )

		self.build.getSettings().set( Settings.ScriptLogLevel, 3 )
		self.build.getSettings().set( Settings.EnvironmentsBaseDir, testMomEnvironments )

	def tearDown( self ):
		MApplication._instance = None

