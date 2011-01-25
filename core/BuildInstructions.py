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

from core.Instructions import Instructions
import os
from core.helpers.GlobalMApp import mApp
from core.Exceptions import ConfigurationError
from core.Settings import Settings
from core.actions.filesystem.MkDirAction import MkDirAction
from core.actions.filesystem.RmDirAction import RmDirAction

class BuildInstructions( Instructions ):
	'''BuildInstructions is the base class for all elements that form the build tree of a project.
	BuildInstructions introduces the build steps.'''

	def prepare( self ):
		'''Execute the prepare phase.
		Sets the packages and reports directories if the script is executed in build or describe mode.'''
		super( BuildInstructions, self ).prepare()
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode in ( Settings.RunMode_Build, Settings.RunMode_Describe ):
			# set base directory
			parentBaseDir = self.getParent().getBaseDir()
			baseDirName = self._getBaseDirName()
			baseDir = os.path.join( parentBaseDir, baseDirName )
			self._setBaseDir( baseDir )
			# set log directory
			logDirName = self._getBaseDirName()
			parentLogDir = self.getParent().getLogDir()
			logDir = os.path.abspath( os.path.join( parentLogDir, logDirName ) )
			self.setLogDir( logDir )
			# set packages directory
			packagesDirName = self._getBaseDirName()
			parentPackageDir = self.getParent().getPackagesDir()
			packagesDir = os.path.abspath( os.path.join( parentPackageDir, packagesDirName ) )
			self.setPackagesDir( packagesDir )
		else:
			self._setBaseDir( os.getcwd() )
			self.setLogDir( os.getcwd() )
		for step in self.calculateBuildSequence():
			self.addStep( step )

	def setup( self ):
		'''Execute the setup phase.
		Creates actions to create the build base directory for this object, and creates the packages and log directories.'''
		super( BuildInstructions, self ).setup()
		# add actions to create the base directory:
		createStep = self.getStep( 'create-folders' )
		createStep.addMainAction( MkDirAction( self.getBaseDir() ) )
		# add action to delete the base directory (but not the log directory):
		cleanupStep = self.getStep( 'build-cleanup' )
		cleanupStep.prependMainAction( RmDirAction( self.getBaseDir() ) )
		# create the log directory
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode == Settings.RunMode_Build:
			try:
				os.makedirs( self.getLogDir() )
			except ( OSError, IOError )as e:
				raise ConfigurationError( 'Cannot create required log directory "{0}" for {1}: {2}!'
										.format( self.getLogDir(), self.getName(), e ) )
			try:
				os.makedirs( self.getPackagesDir() )
			except ( OSError, IOError )as e:
				raise ConfigurationError( 'Cannot create required packages directory "{0}" for {1}: {2}!'
					.format( self.getLogDir(), self.getName(), e ) )
