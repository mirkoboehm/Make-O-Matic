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
from core.Instructions import Instructions
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.executomat.Step import Step
from core.executomat.Action import Action
from core.helpers.TimeKeeper import TimeKeeper
from core.Exceptions import MomError
from core.helpers.FilesystemAccess import make_foldername_from_string
from core.modules.configurations.FolderManager import FolderManager
import os
from core.Project import Project

class _BuildConfigurationAction( Action ):
	def __init__( self, configuration ):
		Action.__init__( self, 'build action for "{0}"'.format( configuration.getName() ) )
		assert configuration
		self.__config = configuration

	def run( self ):
		mApp().debug( self.__config, 'building configuration "{0}"'.format( self.__config.getName() ) )
		self.__config.getTimeKeeper().start()
		mApp().debugN( self, 3, 'saving working directory and environment variables' )
		oldenv = os.environ.copy()
		oldcwd = os.getcwd()
		try:
			self.__config.getExecutomat().run( self.__config )
			return 0
		except MomError as e:
			mApp().message( self.__config, 'error while building configuration "{0}"'.format( e ) )
			# mApp().registerReturnCode( e.getReturnCode() )
			return e.getReturnCode()
		finally:
			os.environ = oldenv
			os.chdir( oldcwd )
			mApp().debugN( self, 3, 'working directory and environment variables restored' )
			self.__config.getTimeKeeper().stop()
			mApp().debug( self.__config, 'finished building configuration "{0}"'.format( self.__config.getName() ) )

	def getLogDescription( self ):
		return self.__config.getName()

class Configuration( Instructions ):
	'''Configuration represents a variant of how a project is built.
	It is always related to a project.'''

	def __init__( self, project, configName ):
		Instructions.__init__( self, configName )
		project.addChild( self )
		self.__timeKeeper = TimeKeeper()
		self.setBaseDir( make_foldername_from_string( configName ) )
		self.__folderManager = FolderManager()
		self.addPlugin( self.__folderManager )

	def getProject( self ):
		assert isinstance( self.getParent(), Project )
		return self.getParent()

	def getFolderManager( self ):
		return self.__folderManager

	def setBaseDir( self, baseDir ):
		self.__baseDir = baseDir

	def getBaseDir( self ):
		return self.__baseDir

	def getTimeKeeper( self ):
		return self.__timeKeeper

	def runSetups( self ):
		for step in self.calculateBuildSequence():
			self.getExecutomat().addStep( step )
		action = _BuildConfigurationAction( self )
		step = self.getProject().getExecutomat().getStep( 'project-build-configurations' )
		step.addMainAction( action )
		Instructions.runSetups( self )

	def calculateBuildSequence( self ):
		buildType = mApp().getSettings().get( Settings.ProjectBuildType, True ).lower()
		allBuildSteps = mApp().getSettings().get( Settings.ConfigurationBuildSteps, True )
		buildSteps = []
		for buildStep in allBuildSteps:
			# FIXME maybe this could be a unit test?
			assert len( buildStep ) == 3
			name, types, executeOnFailure = buildStep
			assert types.lower() == types
			stepName = Step( name )
			stepName.setEnabled( buildType in types )
			stepName.setExecuteOnFailure( executeOnFailure )
			buildSteps.append( stepName )
		assert self.getProject()
		params = self.getProject().getBuild().getParameters()
		params.applyBuildSequenceSwitches( buildSteps, 'conf' )
		return buildSteps

