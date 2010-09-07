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
from core.helpers.TypeCheckers import check_for_path
import shutil
from core.helpers.GlobalMApp import mApp

class RmDirAction( Action ):
	"""RmDirAction deletes a directory."""

	def __init__( self, path, name = None ):
		Action.__init__( self, name )
		self.setPath( path )

	def setPath( self, path ):
		check_for_path( path, "The directory to create must be a non-empty name of a directory!" )
		self.__path = path

	def getPath( self ):
		return self.__path

	# FIXME Are result and the return value redundant? How to enforce setting result?
	def run( self ):
		check_for_path( self.getPath(), "No directory specified!" )
		mApp().debugN( self, 2, 'deleting directory "{0}"'.format( self.getPath() ) )
		try:
			shutil.rmtree( str( self.getPath() ), False )
			return 0
		except ( OSError, IOError ) as e:
			error = 'error deleting directory "{0}": {1}'.format( self.getPath(), str( e ) )
			self._setStdErr( error.encode() )
			mApp().debug( self, error )
			return 1

	def getLogDescription( self ):
		"""Overload"""
		return 'rmdir "{0}"'.format( self.getPath() )
