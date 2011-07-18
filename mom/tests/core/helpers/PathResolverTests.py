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

import os
from core.helpers.PathResolver import PathResolver
import unittest
from mom.tests.helpers.MomTestCase import MomTestCase

class FolderTester( object ):
	def pathMethod( self ):
		return os.getcwd()

class PathResolverTests( MomTestCase ):

	def testPathResolver( self ):
		tester = FolderTester()
		filename = 'test.txt'
		resolver = PathResolver( tester.pathMethod, filename )
		path = str( resolver )
		filepath = os.path.join( os.getcwd(), filename )
		self.assertEqual( path, filepath )
		tmpdir = 'test_folder'
		if os.path.isdir( tmpdir ):
			os.rmdir( tmpdir )
		os.mkdir( tmpdir )
		oldpwd = os.getcwd()
		os.chdir( tmpdir )
		newfilepath = os.path.join( os.getcwd(), filename )
		self.assertEqual( str( resolver ), newfilepath )
		os.chdir( oldpwd )
		os.rmdir( tmpdir )
		self.assertEqual( str( resolver ), filepath )

if __name__ == "__main__":
	unittest.main()
