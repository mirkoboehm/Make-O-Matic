# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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
import unittest
from tests.helpers.MomTestCase import MomTestCase
from core.MomSetup import mom_root_dir
import sys

class EnvironmentSetupTests( MomTestCase ):

	def _getPathPosition( self, path ):
		normalizedPathList = [os.path.abspath( x ) for x in sys.path]

		return normalizedPathList.index( path )

	def testIfTestEnvironmentVariableIsSet( self ):
		self.assertTrue( os.getenv( "MOM_TESTS_RUNNING" ) == "1" )

	def testMomPathCorrectness( self ):
		filePath = os.path.realpath( os.path.dirname( __file__ ) )
		momDirectory = os.path.abspath( os.path.join( filePath, '..', '..' ) )

		pos1 = self._getPathPosition( momDirectory )
		pos2 = self._getPathPosition( mom_root_dir() )
		self.assertTrue( pos1 <= pos2, "We are using the wrong MOM modules! sys.path returns: {0}".format( sys.path ) )

if __name__ == "__main__":
	unittest.main()
