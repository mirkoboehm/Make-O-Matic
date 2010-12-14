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
from core.Project import Project
from core.BuildInstructions import BuildInstructions

class ConfigurationBase( BuildInstructions ):
	'''ConfigurationBase encapsulates common logic of configuration-like objects.'''

	def __init__( self, name, parent = None ):
		BuildInstructions.__init__( self, name, parent )

	def getProject( self ):
		project = self.getParent()
		if not isinstance( project, Project ):
			project = self.getParent().getProject()
		assert isinstance( project, Project )
		return project

	def _stepsShouldExecute( self ):
		'''Override the behavior that defines if Steps should be executed for Configurations.
		Configurations should be built, even if another Configuration produced an error before. Configurations should only be 
		skipped if an error happened in a instructions object, because that might influence the build for the Configuration.'''
		# if there was no problem so far, stick to the base class implementation
		if super( ConfigurationBase, self )._stepsShouldExecute():
			return True
		# check if self or any of the instructions objects caused it
		instructions = self
		while instructions:
			if instructions.hasFailed(): return False
			instructions = instructions.getParent()
		return True

