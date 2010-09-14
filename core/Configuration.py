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
from core.Build import Build
from core.actions.ExecuteConfigurationBaseAction import ExecuteConfigurationBaseAction
from core.Exceptions import MomError
import core
from core.modules.ConfigurationBase import ConfigurationBase
from core.helpers.EnvironmentSaver import EnvironmentSaver
import os
from core.actions.filesystem.MkDirAction import MkDirAction
from core.helpers.PathResolver import PathResolver
from core.actions.filesystem.RmDirAction import RmDirAction

class Configuration( ConfigurationBase ):
	'''Configuration represents a variant of how a project is built.
	It is always related to a project.'''

	def __init__( self, configName, parent = None ):
		ConfigurationBase.__init__( self, configName, parent )

	def _setProject( self, project ):
		assert isinstance( project, core.Project.Project )
		self.__project = project

	def _getNormPath( self, name ):
		path = os.path.join( self.getBaseDir(), mApp().getSettings().get( name ) )
		return os.path.normpath( os.path.abspath( path ) )

	def getBuildDir( self ):
		return self._getNormPath( Settings.ConfigurationBuildDir )

	def getTargetDir( self ):
		return self._getNormPath( Settings.ConfigurationTargetDir )

	def buildConfiguration( self ):
		'''Helper method used by configuration-like objects that executes the whole instructions as part of a step of a superior 
		instructions object.'''
		mApp().debug( self, 'building configuration "{0}"'.format( self.getName() ) )
		with EnvironmentSaver():
			self.getTimeKeeper().start()
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
				self.getTimeKeeper().stop()
				mApp().debug( self, 'finished building configuration "{0}"'.format( self.getName() ) )

	def runSetups( self ):
		for step in self.calculateBuildSequence():
			self.getExecutomat().addStep( step )
		action = ExecuteConfigurationBaseAction( self )
		action.setIgnorePreviousFailure( True )
		try:
			step = self.getParent().getStep( 'project-build-configurations' )
			step.addMainAction( action )
		except MomError:
			mApp().debugN( self, 5, 'parent is not a Project, not generating actions' )
		settings = mApp().getSettings()
		folders = [ settings.get( Settings.ConfigurationBuildDir ), settings.get( Settings.ConfigurationTargetDir ) ]
		create = self.getStep( 'conf-create-folders' )
		cleanup = self.getStep( 'conf-cleanup' )
		for folder in folders:
			create.addMainAction( MkDirAction( PathResolver( self.getBaseDir, folder ) ) )
		folders.reverse()
		for folder in folders:
			cleanup.addMainAction( RmDirAction( PathResolver( self.getBaseDir, folder ) ) )
		ConfigurationBase.runSetups( self )

	def calculateBuildSequence( self ):
		buildSteps = self._setupBuildSteps( Settings.ConfigurationBuildSteps )
		assert isinstance( mApp(), Build )
		mApp().getParameters().applyBuildSequenceSwitches( buildSteps, 'conf' )
		return buildSteps
