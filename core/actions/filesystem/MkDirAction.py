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

from core.executomat.Action import Action
from core.helpers.TypeCheckers import check_for_nonempty_string
import os

class MkDirAction( Action ):
	"""MkDirAction creates a directory.
	The directory will be created local to the working directory of the action."""

	def __init__( self, path = None, name = None ):
		if name == None:
			name = self.__class__.__name__
		Action.__init__( self, name )
		self.setPath( path )

	def setPath( self, path ):
		check_for_nonempty_string( path, "The directory to create must be a non-empty name of a directory!" )
		self.__path = path

	def getPath( self ):
		return self.__path

	def run( self, project ):
		check_for_nonempty_string( self.getPath(), "No directory specified!" )
		project.debugN( 2, '[{0}] creating directory "{1}"'.format( self.getName(), self.getPath() ) )
		# FIXME error handling?
		os.makedirs( self.getPath() )
