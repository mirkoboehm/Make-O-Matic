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

from core.Exceptions import ConfigurationError
from core.plugins.sourcecode import getScm
from core.plugins.sourcecode.SCMGit import SCMGit
from core.plugins.sourcecode.SCMSubversion import SCMSubversion
from mom.tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase
import unittest

class ScmFactoryTests( MomBuildMockupTestCase ):

	def _checkScm( self, url, type ):
		scm = getScm( url )
		if type:
			self.assertTrue( isinstance( scm, type ), 'The descriptor {0} should result in a {1} object!'.format( url, type ) )

	def testCreateGitScm( self ):
		self._checkScm( 'git:git://github.com/KDAB/Make-O-Matic.git', SCMGit )
		self._checkScm( 'git://github.com/KDAB/Make-O-Matic.git', SCMGit )

	def testCreateSvnScm( self ):
		self._checkScm( 'svn:http://svn.github.com/KDAB/Make-O-Matic', SCMSubversion )
		self._checkScm( 'http://svn.github.com/KDAB/Make-O-Matic', SCMSubversion )

	def testCreateUnknownScm( self ):
		try:
			self._checkScm( 'nonsense:nonsense', None )
		except ConfigurationError:
			pass # just as expected
		else:
			self.fail( "Trying to create an unknown source code provider implementation should throw a configuration error!" )

if __name__ == "__main__":
	unittest.main()
