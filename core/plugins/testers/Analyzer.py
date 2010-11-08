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
	def __init__( self, name = None ):
		Plugin.__init__( self, name )

		self.__score = None
		self.__report = None

	def _setScore( self, score, top ):
		self.__score = [ score, top ]

	def _setReport( self, txt ):
		self.__report = txt

	def getScore( self ):
		'''Return a pair of floats representing a score, e.g. "9.29 out of 10". 
		If it returns None, the specific Analyzer does not calculate a score.'''
		return self.__score

	def getReport( self ):
		'''Returns the anaylzer report in human readable format'''

		return self.__report

	def getDescription( self ):
		scoreText = " out of ".join( [str( x ) for x in self.getScore()] ) if self.getScore() else "N/A"
		return "Score: {0}, {1}".format( scoreText, self.getReport() )