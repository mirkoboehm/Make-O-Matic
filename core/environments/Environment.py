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
from core.MObject import MObject
from copy import copy

class Environment( MObject ):
	'''Environment is a single match of the required build environment for a single 
	configuration.'''

	def __init__( self, environments, name = None ):
		MObject.__init__( self, name )
		from core.environments.Environments import Environments
		assert isinstance( environments, Environments )
		self.__environments = environments
		self.__configurations = []

	def cloneConfigurations( self ):
		for configuration in self.__environments.getChildren():
			self.getConfigurations().append( copy( configuration ) )

	def getConfigurations( self ):
		return self.__configurations

	def build( self ):
		'''Apply the environment, build the configuration, restore the environment.'''
		# apply environment:
		# ...
		# build configuration:
		for configuration in self.getConfigurations():
			configuration.buildConfiguration()
		# restore original environment
