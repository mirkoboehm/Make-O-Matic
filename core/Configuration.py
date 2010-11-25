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
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
import core
from core.ConfigurationBase import ConfigurationBase
import os
from core.actions.filesystem.MkDirAction import MkDirAction
from core.helpers.PathResolver import PathResolver
from core.actions.filesystem.RmDirAction import RmDirAction
from core.helpers.TypeCheckers import check_for_string

class Configuration( ConfigurationBase ):
	'''Configuration represents a variant of how a project is built.
	It is always related to a project.'''

	def __init__( self, configName, parent = None ):
		ConfigurationBase.__init__( self, configName, parent )
		self.__sourcePrefix = ""

	def _setProject( self, project ):
		assert isinstance( project, core.Project.Project )
		self.__project = project

	def _getNormPath( self, name ):
		path = os.path.join( self.getBaseDir(), mApp().getSettings().get( name ) )
		return os.path.normpath( os.path.abspath( path ) )

	def getBuildDir( self ):
		return self._getNormPath( Settings.ConfigurationBuildDir )

	def getTagName( self ):
		return "configuration" # prevent subclasses to get individual names

	def getTargetDir( self ):
		return self._getNormPath( Settings.ConfigurationTargetDir )

	def setSourcePrefix( self, sourcePrefix ):
		check_for_string( sourcePrefix, "The source prefix needs to be a string" )
		self.__sourcePrefix = sourcePrefix

	def getSourcePrefix( self ):
		return self.__sourcePrefix

	def setup( self ):
		super( Configuration, self ).setup()
		settings = mApp().getSettings()
		folders = [ settings.get( Settings.ConfigurationBuildDir ), settings.get( Settings.ConfigurationTargetDir ) ]
		create = self.getStep( 'build-create-folders' )
		cleanup = self.getStep( 'build-cleanup' )
		for folder in folders:
			create.addMainAction( MkDirAction( PathResolver( self.getBaseDir, folder ) ) )
		for folder in folders:
			cleanup.prependMainAction( RmDirAction( PathResolver( self.getBaseDir, folder ) ) )

	def clone( self ):
		c = super( Configuration, self ).clone()
		c.setSourcePrefix( self.getSourcePrefix()[:] )
		return c
