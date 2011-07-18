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

from mom.tests.helpers.MomTestCase import MomTestCase
import unittest
from core.plugins.testers.Analyzer import Analyzer

class _MyAnalyzer( Analyzer ):
	"""Inherit Analyzer and make non-public API public"""

	def setScore( self, score, top ):
		self._setScore( score, top )

	def setReport( self, txt ):
		self._setReport( txt )

	def setRequiredMinimumSuccessRate( self, percentage ):
		self._setRequiredMinimumSuccessRate( percentage )

class AnalyzerTests( MomTestCase ):

	def setUp( self ):
		MomTestCase.setUp( self )

		self.analyzer = _MyAnalyzer()

	def testValidScore( self ):
		self.analyzer.setRequiredMinimumSuccessRate( 0.75 )
		self.analyzer.setScore( 7.8, 10.0 )

		self.assertTrue( self.analyzer.isScoreOkay() )

	def testInvalidScore( self ):
		self.analyzer.setRequiredMinimumSuccessRate( 0.85 )
		self.analyzer.setScore( 80, 100 )

		self.assertFalse( self.analyzer.isScoreOkay() )

if __name__ == "__main__":
	unittest.main()
