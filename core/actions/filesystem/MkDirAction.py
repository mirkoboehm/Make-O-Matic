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

from core.helpers.TypeCheckers import check_for_path
import os
from core.helpers.GlobalMApp import mApp
from core.actions.filesystem.DirActionBase import DirActionBase

class MkDirAction( DirActionBase ):
	"""MkDirAction creates a directory.
	The directory will be created local to the working directory of the action."""

	def __init__( self, path, name = None ):
		DirActionBase.__init__( self, path, name )

	def run( self ):
		check_for_path( self.getPath(), "No directory specified!" )
		mApp().debugN( self, 4, 'creating directory "{0}"'.format( self.getPath() ) )
		try:
			os.makedirs( str( self.getPath() ) )
			return 0
		except ( OSError, IOError ) as e:
			error = 'error creating directory "{0}": {1}'.format( self.getPath(), str( e ) )
			self._setStdErr( error.encode() )
			mApp().debug( self, error )
			return 1

	def getLogDescription( self ):
		"""Overload"""
		return 'mkdir "{0}"'.format( self.getPath() )
