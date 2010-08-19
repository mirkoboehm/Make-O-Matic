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
from copy import copy
from core.modules.ConfigurationBase import ConfigurationBase

class Environment( ConfigurationBase ):
	'''Environment is a single match of the required build environment for a single 
	configuration.'''

	def __init__( self, name, parent ):
		ConfigurationBase.__init__( self, name, parent )
		from core.environments.Environments import Environments
		assert isinstance( parent, Environments )

	def _getEnvironments( self ):
		return self.getParent()

	def cloneConfigurations( self, configs ):
		for configuration in configs:
			clone = copy( configuration )
			for plugin in clone.getPlugins():
				plugin._setInstructions( clone )
			self.addChild( clone )

	def build( self ):
		'''Apply the environment, build the configuration, restore the environment.'''
		# apply environment:
		# ...
		# build configuration:
		error = False
		for configuration in self.getChildren():
			if configuration.buildConfiguration() != 0:
				error = True
		# restore original environment
		# ...
		# return result
		if error:
			return 1
		else:
			return 0
