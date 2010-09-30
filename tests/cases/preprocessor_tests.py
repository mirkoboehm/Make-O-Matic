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
from core.plugins.Preprocessor import _PreprocessorAction
from core.Exceptions import BuildError
from tests.helpers.MomTestCase import MomTestCase

class PreprocessorTest( MomTestCase ):

	def _runTest( self, inputString, outputString, msg = None ):
		'''Helper method to run a single test'''
		prep = _PreprocessorAction( None )
		if not msg:
			msg = '{0} should resolve to {1}'.format( inputString, outputString )
		self.assertEqual( outputString, prep.processLine( inputString ), msg )

	def testEmptyinputString( self ):
		self._runTest( '', '', 'An empty input line should result in an empty output line' )

	def testinputStringWithoutPlaceholders( self ):
		inputString = 'hello world'
		outputString = inputString
		self._runTest( inputString, outputString, 'A line without any replacement place holders should return the input string unchanged' )

	def testEscapePattern( self ):
		inputString = '@@(@@)'
		outputString = '@@'
		self._runTest( inputString, outputString )

	def testMultipleEscapePatterns( self ):
		inputString = 's @@(@@) @@(@@) e'
		outputString = 's @@ @@ e'
		self._runTest( inputString, outputString )

	def testUnbalancedBrackets( self ):
		inputString = '@@(@@'
		prep = _PreprocessorAction( None )
		self.assertRaises( BuildError, prep.processLine, inputString )

	def testBalancedAndUnbalancedBrackets( self ):
		inputString = 's @@(@@) @@(@@ e'
		prep = _PreprocessorAction( None )
		self.assertRaises( BuildError, prep.processLine, inputString )

if __name__ == "__main__":
	#import sys;sys.argv = ['', 'PreprocessorTest.testName']
	unittest.main()
