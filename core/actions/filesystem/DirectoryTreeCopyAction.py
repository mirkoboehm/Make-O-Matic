# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
# Author: Andreas Holzammer <andy@kdab.com>
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

from core.actions.Action import Action
from core.helpers.GlobalMApp import mApp
import shutil
from core.Exceptions import ConfigurationError
from core.helpers.TypeCheckers import check_for_list_of_strings
import os

class Error( EnvironmentError ):
    pass

class DirectoryTreeCopyAction( Action ):
	"""DirectoryTreeCopyAction encapsulates the copying of a directory tree 
	to another directory, optionally ignoring some files.
	It is mostly used internally, but can be of general use as well."""
	def __init__( self, source, destination, ignorePatterns = None, overwrite = False ):
		Action.__init__( self )
		self.__source = source
		self.__destination = destination
		self.__overwrite = overwrite
		if ignorePatterns == None:
			ignorePatterns = []
		check_for_list_of_strings( ignorePatterns, "The ignore patterns must be a list of strings." )
		self.__ignorePatterns = ignorePatterns

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return "copytree {0} {1}, ignoring {2}".format( self.__source, self.__destination, self.__ignorePatterns )

	def mycopytree( self, src, dst, ignore = None , overwrite = False ):
		"""Copies the directory tree."""

		names = os.listdir( src )

		if ignore is not None:
			ignored_names = ignore( src, names )
		else:
			ignored_names = set()

		if not os.path.exists( dst ):
			os.makedirs( dst )
		errors = []
		for name in names:
			if name in ignored_names:
				continue
			srcname = os.path.join( src, name )
			dstname = os.path.join( dst, name )
			try:
				if os.path.isdir( srcname ):
					self.mycopytree( srcname, dstname, ignore )
				else:
					if self.__overwrite or not os.path.isfile( dstname ):
						shutil.copy2( srcname, dstname )
					# XXX What about devices, sockets etc.?
			except ( IOError, os.error ), why:
				errors.append( ( srcname, dstname, str( why ) ) )
				# catch the Error from the recursive copytree so that we can
				# continue with other files
			except Error, err:
				errors.extend( err.args[0] )
		try:
			shutil.copystat( src, dst )
		except OSError, why:
			if WindowsError is not None and isinstance( why, WindowsError ):
			# Copying file access times may fail on Windows
				pass
			else:
				errors.extend( ( src, dst, str( why ) ) )
		if errors:
			raise Error, errors

	def run( self ):
		"""Copies the directory tree."""

		self.mycopytree( self.__source, self.__destination, shutil.ignore_patterns( *self.__ignorePatterns ), self.__overwrite )

		mApp().debugN( self, 2, 'copied directory tree "{0}" to "{1}".'.format( self.__source, self.__destination ) )
		return 0
