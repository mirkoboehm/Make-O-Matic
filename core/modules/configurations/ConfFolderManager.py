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
import core
from core.helpers.PathResolver import PathResolver
from core.Settings import Settings
from core.actions.filesystem.MkDirAction import MkDirAction
from core.actions.filesystem.RmDirAction import RmDirAction
from core.helpers.GlobalMApp import mApp

class ConfFolderManager( Plugin ):
	'''ConfFolderManager handles the folders used during the build of a configuration.'''

	def __init__( self, configuration ):
		Plugin.__init__( self )
		assert isinstance( configuration, core.Configuration.Configuration )
		self.__configuration = configuration

	def getConfiguration( self ):
		return self.__configuration

	def setup( self, configuration ):
		settings = mApp().getSettings()
		folders = [ None, settings.get( Settings.ConfigurationBuildDir ), settings.get( Settings.ConfigurationTargetDir )]
		create = configuration.getExecutomat().getStep( 'conf-create-folders' )
		cleanup = configuration.getExecutomat().getStep( 'conf-cleanup' )
		for folder in folders:
			create.addMainAction( MkDirAction( PathResolver( configuration.getBaseDir, folder ) ) )
		folders.reverse()
		for folder in folders:
			cleanup.addMainAction( RmDirAction( PathResolver( configuration.getBaseDir, folder ) ) )
