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
from core.Plugin import Plugin
from core.helpers.PathResolver import PathResolver
from core.Settings import Settings
from core.actions.filesystem.MkDirAction import MkDirAction
from core.actions.filesystem.RmDirAction import RmDirAction
from core.helpers.GlobalMApp import mApp
import os

class FolderManager( Plugin ):
	'''FolderManager handles the folders used during the build of a configuration.'''

	def __init__( self ):
		Plugin.__init__( self )

	def getConfiguration( self ):
		from core.Configuration import Configuration
		assert isinstance( self.getInstructions(), Configuration )
		return self.getInstructions()

	def setup( self ):
		from core.Configuration import Configuration
		configuration = self.getInstructions()
		assert isinstance( configuration, Configuration )
		settings = mApp().getSettings()
		folders = [ settings.get( Settings.ConfigurationBuildDir ), settings.get( Settings.ConfigurationTargetDir ) ]
		create = configuration.getExecutomat().getStep( 'conf-create-folders' )
		cleanup = configuration.getExecutomat().getStep( 'conf-cleanup' )
		for folder in folders:
			create.addMainAction( MkDirAction( PathResolver( configuration.getBaseDir, folder ) ) )
		folders.reverse()
		for folder in folders:
			cleanup.addMainAction( RmDirAction( PathResolver( configuration.getBaseDir, folder ) ) )

	def _getNormPath( self, name ):
		from core.Configuration import Configuration
		configuration = self.getInstructions()
		assert isinstance( configuration, Configuration )
		path = os.path.join( configuration.getBaseDir(), mApp().getSettings().get( name ) )
		return os.path.normpath( os.path.abspath( path ) )

	def getBuildDir( self ):
		return self._getNormPath( Settings.ConfigurationBuildDir )

	def getTargetDir( self ):
		return self._getNormPath( Settings.ConfigurationTargetDir )


