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
from core.Exceptions import ConfigurationError

class StringResolver( object ):

	def __init__( self, pattern = None ):
		self.__pattern = pattern

	def setPattern( self, pattern ):
		self.__pattern = pattern

	def getPattern( self ):
		return self.__pattern

	def __str__( self ):
		value = self._asString()
		if not self.getPattern():
			return str( value )
		else:
			try:
				result = self.getPattern().format( value )
				return result
			except ValueError:
				raise ConfigurationError( 'The StringResolver "{0}" pattern needs to contain exactly one place holder like this: '\
					.format( self.getPattern() ) + '"pattern-{0}"' )
