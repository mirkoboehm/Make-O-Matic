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
import sys
from core.loggers.Logger import Logger
from core.helpers.TypeCheckers import check_for_nonnegative_int

class ConsoleLogger( Logger ):
	"""ConsoleLogger prints status and debug messages to the stderr stream."""

	def __init__( self, level = 0 ):
		"""Constructor"""
		Logger.__init__( self, self.__class__.__name__ )
		self.setLevel( level )

	def setLevel( self, level ):
		check_for_nonnegative_int( level, "The debug level needs to be an integer of zero or more" )
		self.__level = level

	def getLevel( self ):
		return self.__level

	def message( self, mobject, msg ):
		text = str( msg )
		if not text.endswith( '\n' ): text = text + '\n'
		fulltext = '{0} {1}[{2}] {3}'.format( self.timeStampPrefix(), self.messagePrefix(), mobject.getName(), text )
		sys.stderr.write( fulltext )

	def debug( self, mobject, msg ):
		text = str( msg )
		if self.getLevel() > 0:
			self.message( mobject, 'DEBUG: ' + str( text ) )

	def debugN( self, mobject, level , msg ):
		if self.getLevel() >= level:
			self.debug( mobject, msg )
