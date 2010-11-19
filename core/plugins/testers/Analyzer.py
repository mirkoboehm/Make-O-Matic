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

from core.Plugin import Plugin

class Analyzer( Plugin ):
	def __init__( self, name = None, minimumScore = 0.0 ):
		Plugin.__init__( self, name )

		self.__score = None
		self.__report = None
		self._setMinimumScore( minimumScore )

	def _setScore( self, score, top ):
		self.__score = [ score, top ]

	def _setReport( self, txt ):
		self.__report = txt

	def getScore( self ):
		'''Return a pair of floats representing a score, e.g. "9.29 out of 10". 
		If it returns None, the specific Analyzer does not calculate a score.'''

		return self.__score

	def getReport( self ):
		'''Returns the analyzer report in human readable format'''

		return self.__report

	def _setMinimumScore( self, minimumScore ):
		self.__minimumScore = minimumScore

	def getMinimumScore( self ):
		return self.__minimumScore

	def isScoreOkay( self ):
		if not self.getScore():
			return True # score is None => no score calculated => okay

		return ( self.getScore()[0] >= self.getMinimumScore() )

	def getDescription( self ):
		if not self.getInstructions().getStep( "conf-make-test" ).isEnabled():
			return "Step disabled"

		scoreText = " out of ".join( [str( x ) for x in self.getScore()] ) if self.getScore() else "N/A"
		scoreOkayText = "skipped" if not self.getScore() else ( "passed" if self.isScoreOkay() else "FAILED" )
		return "Score: {0} -> {1}. Report: {2}".format( scoreText, scoreOkayText, self.getReport() )
