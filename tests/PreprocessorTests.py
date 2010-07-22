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
from core.modules.Preprocessor import _PreprocessorAction

class Test( unittest.TestCase ):

	def _runTest( self, input, output, msg ):
		'''Helper method to run a single test'''
		prep = _PreprocessorAction( None )
		self.assertEqual( output, prep.processLine( input ) )

	def testEmptyInput( self ):
		self._runTest( '', '', 'An empty input line should result in an empty output line' )

	def testInputWithoutPlaceholders( self ):
		input = 'hello world'
		output = input
		self._runTest( input, output, 'A line without any replacement place holders should return the input string unchanged' )


if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
