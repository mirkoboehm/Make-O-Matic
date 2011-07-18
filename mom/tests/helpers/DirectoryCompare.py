# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko.boehm@kdab.com>
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
import os

class DirectoryCompare( object ):
	'''DirectoryCompare stores the contents of a directory, and later compares it with the stored state.
	If the directory changed, an exception is thrown.'''

	def __init__( self, path ):
		self.__path = path

	def __enter__( self ):
		self.__elements = set( os.listdir( self.__path ) )

	def __exit__( self, type, value, traceback ):
		elements = set( os.listdir( self.__path ) )
		if elements != self.__elements:
			diff = self.__elements ^ elements
			raise Exception( 'The watched directory has changed, new entries: {0}'.format( ', '.join( diff ) ) )
