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

import unittest
from core.modules.scm.Factory import SourceCodeProviderFactory
from core.Project import Project
from core.modules.scm.SCMGit import SCMGit
from core.Settings import Settings
from core.Exceptions import ConfigurationError
from core.Build import Build
from tests.helpers.MomTestCase import MomTestCase

class ScmFactoryTests( MomTestCase ):

	def setUp( self ):
		MomTestCase.setUp( self, False )
		self.build = Build()
		self.project = Project( 'ScmFactoryTest' )
		self.build.setProject( self.project )
		self.build.getSettings().set( Settings.ScriptLogLevel, 3 )
		self.project.createScm( 'git:git://github.com/mirkoboehm/Make-O-Matic.git' )

	def createAndReturnScm( self, description ):
		return SourceCodeProviderFactory().makeScmImplementation( description )

	def testCreateGitScm( self ):
		description = 'git:git://github.com/mirkoboehm/Make-O-Matic.git'
		scm = self.createAndReturnScm( description )
		self.assertTrue( isinstance( scm, SCMGit ), 'The descriptor {0} should result in a ScmGit object!'.format( description ) )

	def testCreateUnknownScm( self ):
		try:
			self.createAndReturnScm( 'nonsense:more nonsense' )
		except ConfigurationError:
			pass # just as expected
		else:
			self.fail( "Trying to create an unknown source code provider implementation should throw a configuration error!" )

if __name__ == "__main__":
	unittest.main()
