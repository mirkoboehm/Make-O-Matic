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

from core.actions.Action import Action
from core.helpers.GlobalMApp import mApp
import shutil
from core.Exceptions import ConfigurationError
from core.helpers.TypeCheckers import check_for_list_of_strings
import os

class DirectoryTreeCopyAction( Action ):
	"""DirectoryTreeCopyAction encapsulates the copying of a directory tree 
	to another directory, optionally ignoring some files.
	It is mostly used internally, but can be of general use as well."""
	def __init__( self, source, destination, ignorePatterns = None ):
		Action.__init__( self )
		self.__source = source
		self.__destination = destination
		if ignorePatterns == None:
			ignorePatterns = []
		check_for_list_of_strings( ignorePatterns, "The ignore patterns must be a list of strings." )
		self.__ignorePatterns = ignorePatterns

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return "copytree {0} {1}, ignoring {2}".format( self.__source, self.__destination, self.__ignorePatterns )

	def run( self ):
		"""Copies the directory tree."""
		try:
			# This will only remove it if the directory is empty. Needed for copytree to work.
			os.rmdir( self.__destination )
			shutil.copytree( self.__source, self.__destination,
							shutil.ignore_patterns( self.__ignorePatterns ) )
		except ( OSError, shutil.Error ) as o:
			raise ConfigurationError( 'Cannot copy directory tree "{0}" to "{1}": {2}'
					.format( self.__source, self.__destination, str( o ) ) )
		mApp().debugN( self, 2, 'copied directory tree "{0}" to "{1}".'.format( self.__source, self.__destination ) )
		return 0
