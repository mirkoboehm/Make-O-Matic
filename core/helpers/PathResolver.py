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
import os
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none

class PathResolver( object ):
	'''A path resolver resolves a project filename to its full path at the time it is converted to a string.
	It calls a function that must return a path, and extends that path with the filename.'''

	def __init__( self, function, filename = None ):
		self.setFunction( function )
		self.setFilename( filename )

	def setFilename( self, filename ):
		check_for_nonempty_string_or_none( filename, 'The filename has to be a non-empty string, or None!' )
		self.__filename = filename

	def getFilename( self ):
		return self.__filename

	def setFunction( self, function ):
		# FIXME how to check that function is callable?
		self.__function = function

	def getFunction( self ):
		return self.__function

	def __str__( self ):
		if( self.getFilename() ):
			return os.path.join( self.getFunction()(), self.getFilename() )
		else:
			return os.path.join( self.getFunction()() )