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

from __future__ import print_function

from core.modules.FolderManager import FolderManager
from core.modules.SourceCodeProvider import SourceCodeProvider
from core.helpers.TimeKeeper import TimeKeeper
from core.Settings import Settings
from core.Exceptions import MomError
from core.modules.scm.Factory import SourceCodeProviderFactory
from core.helpers.PathResolver import PathResolver
from core.Instructions import Instructions
from core.helpers.GlobalMApp import mApp
from core.executomat.Step import Step

"""A Project represents an entity to build. 
FIXME documentation
"""
class Project( Instructions ):

	def __init__( self, projectName ):
		"""Set up the build steps, parse the command line arguments."""
		Instructions.__init__( self, projectName )
		self.setBuild( None )
		mApp().getSettings().set( Settings.ProjectName, projectName )
		self.__timeKeeper = TimeKeeper()
		self.__scm = None
		self.__folderManager = FolderManager( self )
		self.addPlugin( self.getFolderManager() )

	def setBuild( self, build ):
		self.__build = build

	def getBuild( self ):
		return self.__build

	def createScm( self, description ):
		factory = SourceCodeProviderFactory()
		scm = factory.makeScmImplementation( description )
		scm.setSrcDir( PathResolver( self.getFolderManager().getSourceDir ) )
		self.setScm( scm )

	def setScm( self, scm ):
		if self.getScm():
			raise MomError( 'The master SCM can only be set once!' )
		if not isinstance( scm, SourceCodeProvider ):
			raise MomError( 'SCMs need to re-implement the SourceCodeProvider class!' )
		self.__scm = scm
		self.addPlugin( scm )

	def getScm( self ):
		return self.__scm

	def getFolderManager( self ):
		return self.__folderManager

	def getTimeKeeper( self ):
		return self.__timeKeeper

	def runSetups( self ):
		for step in self.calculateBuildSequence( self ):
			self.getExecutomat().addStep( step )
		Instructions.runSetups( self )

	def calculateBuildSequence( self, project ):
		assert self.getBuild()
		buildType = mApp().getSettings().get( Settings.ProjectBuildType, True ).lower()
		assert len( buildType ) == 1
		allBuildSteps = mApp().getSettings().get( Settings.ProjectBuildSteps, True )
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
		mApp().debug( self, 'build type: {0} ({1})'
			.format( buildType.upper(), mApp().getSettings().getBuildTypeDescription( buildType ) ) )
		# apply customizations passed as command line parameters:
		self.getBuild().getParameters().applyBuildSequenceSwitches( buildSteps, 'project' )
		return buildSteps

	def execute( self ):
		self.getTimeKeeper().start()
		try:
			self.getExecutomat().run( self )
		finally:
			self.getTimeKeeper().stop()
