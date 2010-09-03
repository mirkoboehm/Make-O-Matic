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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import unittest
from core.modules.reporters.EmailReporter import EmailReporter
from core.MApplication import MApplication
import inspect
import sys
import os
from core.helpers.BoilerPlate import setupStandardBuild
from core.Project import Project
from core.Settings import Settings
from core.modules.packagers.CPack import CPack
from core.modules.testers.CTest import CTest
from core.modules.tools.cmake.CMakeBuilder import CMakeBuilder
from core.Configuration import Configuration
from core.environments.Environments import Environments

class Test( unittest.TestCase ):

	def setUp( self ):
		if MApplication._instance:
			# do not try this at home!
			MApplication._instance = None

		self.build = None
		self.project = None
		self._initializeBuildMockup()

	def tearDown( self ):
		MApplication._instance = None

	def _initializeBuildMockup( self ):
		myFile = inspect.getfile( inspect.currentframe() )
		myFilePath = os.path.split( myFile )
		myDir = myFilePath[0]
		testMomEnvironments = os.path.join( myDir, 'test-mom-environments' )
		#args = sys.argv.copy()
		sys.argv = []
		build = setupStandardBuild( 'XmlReportTestBuild' )
		project = Project( 'XmlReportTestProject', build )
		project.createScm( 'git:git@gitorious.org:make-o-matic/mom.git' )
		environments = Environments( [ 'Qt-4.[67].?-Shared-*' ], 'Qt 4', project )

		debug = Configuration( 'Debug', environments, )
		cmakeDebug = CMakeBuilder()
		cmakeDebug.setMakeOptions( '-j2' )
		cmakeDebug.setMakeInstallOptions( '-j1' )
		debug.addPlugin( cmakeDebug )

		release = Configuration( 'Release', environments )
		cmakeRelease = CMakeBuilder()
		cmakeRelease.setMakeOptions( '-j2' )
		cmakeDebug.setMakeInstallOptions( '-j1' )
		release.addPlugin( cmakeRelease )
		release.addPlugin( CTest() )
		release.addPlugin( CPack() )

		build.getSettings().set( Settings.ScriptLogLevel, 3 )
		build.getSettings().set( Settings.EnvironmentsBaseDir, testMomEnvironments )

		# add EmailReporter plugin
		build.addPlugin( EmailReporter() )

		self.build = build
		self.project = project

	def testEmailReporterPlugin( self ):
		# TODO: Modify email recipients list for testing

		self.build.runPreFlightChecks()
		self.build.runSetups()
		self.build.buildAndReturn()

if __name__ == "__main__":
	unittest.main()
