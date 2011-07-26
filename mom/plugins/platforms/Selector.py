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
from mom.core.Plugin import Plugin
import os
from mom.core.Exceptions import ConfigurationError
import re

class Selector( Plugin ):
	"""Selector is the base class for the platform WhiteLister and BlackLister classes.
	These classes are used to prevent or allow builds under specific circumstances without raising errors."""
	def __init__( self, variable = None, pattern = None, required = None , name = None ):
		Plugin.__init__( self, name )
		self.setVariableName( variable )
		self.setValuePattern( pattern )
		self.setVariableRequired( required )

	def setVariableName( self, name ):
		self.__variableName = name

	def getVariableName( self ):
		return self.__variableName

	def setValuePattern( self, pattern ):
		self.__pattern = pattern

	def getValuePattern( self ):
		return self.__pattern

	def setVariableRequired( self, onOff ):
		self.__required = onOff

	def getVariableRequired( self ):
		return self.__required

	def _getVariable( self ):
		if os.environ.has_key( self.getVariableName() ):
			return os.environ[ self.getVariableName() ]
		else:
			if self.getVariableRequired():
				text = 'The required environment variable "{0}" is not defined!'.format( self.getVariableName() )
				raise ConfigurationError( text )
			else:
				return None

	def _isMatch( self ):
		"""Return if the variable matches the defined pattern.
		@return False if the variable is not set
		"""
		variable = self._getVariable()
		if not variable:
			return False
		if( re.match( self.getValuePattern(), variable ) ):
			return True
		else:
			return False
