# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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

from tests.helpers.MomTestCase import MomTestCase
import unittest
from core.plugins.python.PyUnitTester import PyUnitTester
import sys

class PyUnitTesterTest( MomTestCase ):

	STR1 = """Ran 3 tests in 0.011s
		FAILED (failures=1, errors=2)"""

	STR2 = """Ran 3 tests in 0.011s
		FAILED (errors=2)"""

	STR3 = """Ran 3 tests in 0.011s
		FAILED (failures=1)"""

	STR4 = """Ran 3 tests in 0.011s
		OK"""

	def setUp( self ):
		MomTestCase.setUp( self, False )
		self.tester = PyUnitTester( sys.executable ) # just use the executable, not used anyway

	# this is for producing the output on failures/errors
#	def testAddFailure( self ):
#		self.assertTrue( False )

#	def testAddException( self ):
#		from core.Exceptions import MomError
#		raise MomError( "" )

	def testParseStr1( self ):
		score, total = self.tester.parseOutput( self.STR1 )
		self.assertEquals( score, 0 ) # means: 0 test succeeded
		self.assertEquals( total, 3 ) # means: 3 tests in total

	def testParseStr2( self ):
		score, total = self.tester.parseOutput( self.STR2 )
		self.assertEquals( score, 1 )
		self.assertEquals( total, 3 ) # means: 3 tests in total

	def testParseStr3( self ):
		score, total = self.tester.parseOutput( self.STR3 )
		self.assertEquals( score, 2 )
		self.assertEquals( total, 3 ) # means: 3 tests in total

	def testParseStr4( self ):
		score, total = self.tester.parseOutput( self.STR4 )
		self.assertEquals( score, 3 )
		self.assertEquals( total, 3 ) # means: 3 tests in total

if __name__ == "__main__":
	unittest.main()
