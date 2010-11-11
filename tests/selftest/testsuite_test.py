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
from unittest import TestCase, main
from core.MomSetup import mom_root_dir
import os

class TestSuiteTest( TestCase ):
	'''This test asserts that the unit tests are executed against the Make-O-Matic modules that came with it. 
	On systems where Make-O-Matic is deployed, another installation is usually in the PYTHONPATH (the one that executes 
	the build script). To run the test suite against the code it shipped with, it's own mom_root_dir() needs to be 
	added to the PYTHONPATH before the path of the installed Make-O-Matic. Otherwise, this test will fail.
	
	The testsuite_selftest.py script in tests/ will automatically manipulate the PYTHONPATH so that this test should 
	succeed.'''

	def testPythonPath( self ):
		directoryFromWhereMomIsImported = mom_root_dir()
		filePath = os.path.realpath( os.path.dirname( __file__ ) )
		myMomDirectory = os.path.abspath( os.path.join( filePath, '..', '..' ) )
		self.assertEqual( directoryFromWhereMomIsImported, myMomDirectory )

if __name__ == "__main__":
	main()

