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
from core.modules.scm.Factory import SourceCodeProviderFactory
from core.Project import Project
from core.modules.scm.SCMGit import SCMGit
from core.Settings import Settings
from core.Exceptions import ConfigurationError
from core.Build import Build
from core.MApplication import MApplication

class ScmFactoryTests( unittest.TestCase ):

	def setUp( self ):
		if MApplication._instance:
			# do not try this at home!
			MApplication._instance = None
		self.build = Build()
		self.project = Project( 'ScmFactoryTest' )
		self.build.setProject( self.project )
		self.build.getSettings().set( Settings.ScriptLogLevel, 3 )
		# self.build.addLogger( ConsoleLogger() )
		self.project.createScm( 'git:git://gitorious.org/make-o-matic/mom.git' )

	def tearDown( self ):
		MApplication._instance = None

	def __createAndReturnScm( self, description ):
		factory = SourceCodeProviderFactory()
		return factory.makeScmImplementation( description )

	def testCreateGitScm( self ):
		description = 'git:git://gitorious.org/make-o-matic/mom.git'
		scm = self.__createAndReturnScm( description )
		self.assertTrue( isinstance( scm, SCMGit ), 'The descriptor {0} should result in a ScmGit object!'.format( description ) )

	def testCreateUnknownScm( self ):
		description = 'nonsense:more nonsense'
		try:
			self.__createAndReturnScm( description )
		except ConfigurationError:
			pass # just as expected
		else:
			self.fail( "Trying to create an unknown source code provider implementation should throw a configuration error!" )

if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
