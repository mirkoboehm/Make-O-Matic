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
import os
from tests.helpers.DirectoryCompare import DirectoryCompare
import sys
from tests.helpers.MomTestCase import MomTestCase
from subprocess import Popen, PIPE

class RunModeDescribeTests( MomTestCase ):

	_THISFILEPATH = os.path.realpath( os.path.dirname( __file__ ) )
	_BUILDSCRIPT = os.path.join( _THISFILEPATH, '..', 'buildscripts', 'example_charm.py' )

	def testDescribe( self ):
		with DirectoryCompare( os.getcwd() ):
			process = Popen( [ sys.executable, self._BUILDSCRIPT, '-t', 'M', 'describe' ], stdout = PIPE, stderr = PIPE )
			stdout, stderr = process.communicate()
			returncode = process.wait()

			self.assertTrue( returncode == 0,
					'The example charm build script fails to execute in describe mode: {0} {1}'
						.format( stdout, stderr ) )

			# describe output should be somewhat lengthy, check this
			self.assertTrue( len( stdout ) > 100, "Output is too short" )

if __name__ == "__main__":
	unittest.main()
