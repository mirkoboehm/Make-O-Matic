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

from core.environments.Environment import Environment
from core.actions.ExecuteConfigurationBaseAction import ExecuteConfigurationBaseAction
from core.modules.ConfigurationBase import ConfigurationBase

class Environments( ConfigurationBase ):
	'''Environments is a decorator for Configuration. It takes a configuration, and a list of required folders, and detects matches 
	of the required folders with those found in the environments base directory.
	The configuration is then cloned for every matching environment, if this functionality is enabled for the selected build type.
	'''

	def __init__( self, dependencies = None, name = None, parent = None ):
		ConfigurationBase.__init__( self, name, parent )
		self._setDependencies( dependencies )
		self._setEnvironments( [] )

	def _setEnvironments( self, envs ):
		self.__environments = envs

	def addEnvironment( self, environment ):
		self.__environments.append( environment )

	def getEnvironments( self ):
		return self.__environments

	def _setDependencies( self, deps ):
		self.__dependencies = deps

	def getDependencies( self ):
		return self.__dependencies

	def buildConfiguration( self ):
		'''For every environment found during setup, apply the environment, and build the configuration.'''
		for environment in self.getEnvironments():
			environment.build()

	def runSetups( self ):
		try:
			action = ExecuteConfigurationBaseAction( self )
			action.setIgnorePreviousFailure( True ) # there may be multiple configurations
			step = self.getParent().getExecutomat().getStep( 'project-build-configurations' )
			step.addMainAction( action )
		except Exception as e:
			print( e )
		ConfigurationBase.runSetups( self )
		# discover matching environments:
		environments = [ Environment( self ) ] # FIXME
		for environment in environments:
			environment.cloneConfigurations()
			self.addEnvironment( environment )
		# FIXME register action to build the environments, which will each build their configuration clone
		ConfigurationBase.runSetups( self )
