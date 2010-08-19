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
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.executomat.Step import Step
from core.helpers.FilesystemAccess import make_foldername_from_string
from core.modules.configurations.FolderManager import FolderManager
from core.Build import Build
from core.actions.ExecuteConfigurationBaseAction import ExecuteConfigurationBaseAction
from core.Exceptions import MomError
import core
from core.modules.ConfigurationBase import ConfigurationBase
import os

class Configuration( ConfigurationBase ):
	'''Configuration represents a variant of how a project is built.
	It is always related to a project.'''

	def __init__( self, configName, parent = None ):
		ConfigurationBase.__init__( self, configName, parent )
		# self._setBaseDir( make_foldername_from_string( configName ) )
		self.__folderManager = FolderManager()
		self.addPlugin( self.__folderManager )

	def getFolderManager( self ):
		return self.__folderManager

	def _setProject( self, project ):
		assert isinstance( project, core.Project.Project )
		self.__project = project

	def buildConfiguration( self ):
		'''Helper method used by configuration-like objects that executes the whole instructions as part of a step of a superior 
		instructions object.'''
		mApp().debug( self, 'building configuration "{0}"'.format( self.getName() ) )
		self.getTimeKeeper().start()
		mApp().debugN( self, 3, 'saving working directory and environment variables' )
		oldenv = os.environ.copy()
		oldcwd = os.getcwd()
		try:
			self.getExecutomat().run( self )
			if self.getExecutomat().hasFailed():
				return 1
			else:
				return 0
		except MomError as e:
			mApp().message( self, 'error while building configuration "{0}"'.format( e ) )
			# mApp().registerReturnCode( e.getReturnCode() )
			return e.getReturnCode()
		finally:
			os.environ = oldenv
			os.chdir( oldcwd )
			mApp().debugN( self, 3, 'working directory and environment variables restored' )
			self.getTimeKeeper().stop()
			mApp().debug( self, 'finished building configuration "{0}"'.format( self.getName() ) )

	def runSetups( self ):
		for step in self.calculateBuildSequence():
			self.getExecutomat().addStep( step )
		action = ExecuteConfigurationBaseAction( self )
		action.setIgnorePreviousFailure( True )
		try:
			step = self.getParent().getExecutomat().getStep( 'project-build-configurations' )
			step.addMainAction( action )
		except MomError:
			mApp().debugN( self, 5, 'parent is not a Project, not generating actions' )
		ConfigurationBase.runSetups( self )

	def calculateBuildSequence( self ):
		buildType = mApp().getSettings().get( Settings.ProjectBuildType, True ).lower()
		allBuildSteps = mApp().getSettings().get( Settings.ConfigurationBuildSteps, True )
		buildSteps = []
		for buildStep in allBuildSteps:
			# FIXME maybe this could be a unit test?
			assert len( buildStep ) == 3
			name, types, ignorePreviousFailure = buildStep
			assert types.lower() == types
			stepName = Step( name )
			stepName.setEnabled( buildType in types )
			stepName.setIgnorePreviousFailure( ignorePreviousFailure )
			buildSteps.append( stepName )
		assert isinstance( mApp(), Build )
		params = mApp().getParameters()
		params.applyBuildSequenceSwitches( buildSteps, 'conf' )
		return buildSteps

