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

class Configuration( Instructions ):
	'''Configuration represents a variant of how a project is built.
	It is always related to a project.'''

	def __init__( self, configName ):
		Instructions.__init__( self, configName )
		self.setProject( None )

	def setProject( self, project ):
		self.__project = project

	def getProject( self ):
		return self.__project

	def runSetups( self ):
		for step in self.calculateBuildSequence():
			self.getExecutomat().addStep( step )
		# FIXME add action to build this configuration to the project
		Instructions.runSetups( self )

	def calculateBuildSequence( self ):
		assert self.getProject()
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
		return buildSteps

