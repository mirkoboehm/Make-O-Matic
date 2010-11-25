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
from core.ConfigurationBase import ConfigurationBase
from core.helpers.EnvironmentSaver import EnvironmentSaver

class Environment( ConfigurationBase ):
	'''Environment is a single match of the required build environment for a single 
	configuration.'''

	def __init__( self, name = None, parent = None ):
		ConfigurationBase.__init__( self, name, parent )
		from core.environments.Environments import Environments
		assert isinstance( parent, Environments )
		self.setDependencies( [] )

	def _getEnvironments( self ):
		return self.getParent()

	def cloneConfigurations( self, configs ):
		for configuration in configs:
			# cloning needs to be done before the steps are created
			assert not configuration.getSteps()
			clone = configuration.clone()
			for plugin in clone.getPlugins():
				plugin.setInstructions( clone )
			self.addChild( clone )

	def setDependencies( self, deps ):
		self.__deps = deps

	def getDependencies( self ):
		return self.__deps

	def addDependency( self, dep ):
		assert dep not in self.__deps
		self.__deps.append( dep )

	def _executeStepRecursively( self, instructions, name ):
		'''Apply the environment, call the base class method, restore the environment.'''
		with EnvironmentSaver():
			# apply environment:
			for dep in self.getDependencies():
				dep.apply()
			# build configuration (error handling is done in the configuration)
			ConfigurationBase._executeStepRecursively( self, instructions, name )

	def makeDescription( self ):
		names = []
		for dep in self.getDependencies():
			names.append( dep.getDescription() )
		return ' - '.join( names )

	def clone( self ):
		c = super( Environment, self ).clone()
		c.setDependencies( self.getDependencies() [:] )
		return c
