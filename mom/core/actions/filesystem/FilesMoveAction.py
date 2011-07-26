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

from mom.core.actions.Action import Action
from shutil import move, Error
from mom.core.helpers.GlobalMApp import mApp
from os.path import isdir

class FilesMoveAction( Action ):
	"""FilesMoveAction encapsulates the moving of files to a directory.
	It is mostly used internally, but can be of general use as well."""
	def __init__( self, files = None, destination = None ):
		Action.__init__( self )
		self.setFiles( files )
		self.setDestination( destination )

	def setFiles( self, sourceFiles ):
		"""Set the list of files to move"""
		self.__sourceFiles = sourceFiles

	def getFiles( self ):
		"""Get the list of files to move"""
		return self.__sourceFiles

	def setDestination( self, destination ):
		"""Set the destination directory to move to"""
		self.__destination = destination

	def getDestination( self ):
		"""Get the destination directory to move to"""
		return self.__destination

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return self.getName()

	def run( self ):
		"""Executes the shell command. Needs a command to be set."""
		if not isdir( str( self.__destination ) ):
			err = 'Could not move files to {0}: {0} is not a directory.'.format( self.__destination )
			self._setStdErr( err.encode() )
			mApp().debug( self, err )
			return 1

		for sourceFile in self.__sourceFiles:
			try:
				mApp().debugN( self, 4, 'moving file from "{0}" to "{1}'.format( sourceFile, self.__destination ) )
				move( sourceFile, self.__destination )
			except Error as e:
				err = 'Could not move file from {0} to {1}: {2}'.format( sourceFile, self.__destination, str( e ) )
				self._setStdErr( err.encode() )
				mApp().debug( self, err )
				return 1
		return 0
