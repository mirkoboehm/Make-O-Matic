# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2011 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Andreas Holzammer <andreas.holzammer@kdab.com>
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
from core.helpers.TypeCheckers import check_for_path
import os
from core.helpers.GlobalMApp import mApp

class CheckDirectoryExistsAction( Action ):
	"""Checks weather a Directory exists"""

	def __init__( self, path, name = None ):
		Action.__init__( self, name )
		self.setPath( path )

	def setPath( self, path ):
		check_for_path( path, "The directory to create must be a non-empty name of a directory!" )
		self.__path = path

	def getPath( self ):
		return self.__path

	def run( self ):
		check_for_path( self.getPath(), "No directory specified!" )
		mApp().debugN( self, 4, 'checking directory "{0}"'.format( self.getPath() ) )
		if ( os.path.exists( str( self.getPath() ) ) ):
			return 0
		else:
			return 1

	def getLogDescription( self ):
		"""Overload"""
		return 'check "{0}" exists'.format( self.getPath() )
