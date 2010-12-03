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
from core.Instructions import Instructions
import os
from core.helpers.GlobalMApp import mApp
from core.Exceptions import MomError, BuildError, ConfigurationError
from core.helpers.TimeKeeper import formatted_time, TimeKeeper
from core.Settings import Settings
from core.helpers.TypeCheckers import check_for_nonempty_string
from core.executomat.Step import Step
from core.actions.filesystem.MkDirAction import MkDirAction
from core.actions.filesystem.RmDirAction import RmDirAction
from copy import deepcopy

class BuildInstructions( Instructions ):
	'''BuildInstructions is the base class for all elements that form the build tree of a project.
	BuildInstructions introduces the build steps.'''

	def __init__( self, name = None, parent = None ):
		'''Constructor.'''
		Instructions.__init__( self, name, parent )
		self.__steps = []
		self.__timeKeeper = TimeKeeper()

	def __deepcopy__( self, memo ):
		'''Customize the behaviour of deepcopy to not include the parent object.'''
		clone = super( BuildInstructions, self ).__deepcopy__( memo )
		clone.__timeKeeper = deepcopy( self.__timeKeeper, memo )
		clone.__steps = deepcopy( self.__steps, memo )
		return clone

	def getFailedStep( self ):
		'''Return the first step that failed during execution, or None.'''
		for step in self.getSteps():
			if step.hasFailed():
				return step
		return None

	def hasFailed( self ):
		'''Returns True if any action of the build steps for this object has failed.'''
		return self.getFailedStep() != None

	def __hasStep( self, stepName ):
		'''Returns True if a step with the specified name already exists.'''
		try:
			self.getStep( stepName )
			return True
		except MomError:
			return False

	def addStep( self, newStep ):
		"""Add a newStep identified by identifier. If the identifier already exists, the new 
		command replaces the old one."""
		if not isinstance( newStep, Step ):
			raise MomError( 'only Step instances can be added to the queue' )
		check_for_nonempty_string( newStep.getName(), "Every step must have a name!" )
		if self.__hasStep( newStep.getName() ):
			raise MomError( 'A step with the name {0} already exists for this Instructions object!'.format( newStep.getName() ) )
		self.__steps.append( newStep )

	def getSteps( self ):
		'''Return the list of build steps for the object.
		It is a list, not a dictionary, because the steps are a sequence and cannot be reordered.'''
		return self.__steps

	def getStep( self, identifier ):
		"""Find the step with this identifier and return it."""
		for step in self.getSteps():
			if step.getName() == identifier:
				return step
		raise MomError( 'no such step "{0}"'.format( identifier ) )

	def getTimeKeeper( self ):
		'''Return the TimeKeeper object to measure execution time.'''
		return self.__timeKeeper

	def describe( self, prefix, details = None ):
		'''Print describe output.'''
		Instructions.describe( self, prefix )
		for step in self.getSteps():
				step.describe( prefix + '    ' )

	def createXmlNode( self, document ):
		'''Create a node for the XML report.'''
		node = Instructions.createXmlNode( self, document )
		node.attributes["starttime"] = str ( formatted_time( self.getTimeKeeper().getStartTime() ) )
		node.attributes["stoptime"] = str ( formatted_time( self.getTimeKeeper().getStopTime() ) )
		node.attributes["timing"] = str( self.getTimeKeeper().deltaString() )
		node.attributes["failed"] = str( self.hasFailed() )

		stepsElement = document.createElement( "steps" )
		for step in self.getSteps():
			element = step.createXmlNode( document )
			stepsElement.appendChild( element )
		node.appendChild( stepsElement )

		return node

	def prepare( self ):
		'''Execute the prepare phase.
		Sets the packages and reports directories if the script is executed in build or describe mode.'''
		super( BuildInstructions, self ).prepare()
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode in ( Settings.RunMode_Build, Settings.RunMode_Describe ):
			# set base directory
			parentBaseDir = self.getParent().getBaseDir()
			baseDirName = self._getBaseDirName()
			baseDir = os.path.join( parentBaseDir, baseDirName )
			self._setBaseDir( baseDir )
			# set log directory
			logDirName = self._getBaseDirName()
			parentLogDir = self.getParent().getLogDir()
			logDir = os.path.abspath( os.path.join( parentLogDir, logDirName ) )
			self.setLogDir( logDir )
			# set packages directory
			packagesDirName = self._getBaseDirName()
			parentPackageDir = self.getParent().getPackagesDir()
			packagesDir = os.path.abspath( os.path.join( parentPackageDir, packagesDirName ) )
			self.setPackagesDir( packagesDir )
		else:
			self._setBaseDir( os.getcwd() )
			self.setLogDir( os.getcwd() )
		for step in self.calculateBuildSequence():
			self.addStep( step )

	def setup( self ):
		'''Execute the setup phase.
		Creates actions to create the build base directory for this object, and creates the packages and log directories.'''
		super( BuildInstructions, self ).setup()
		# add actions to create the base directory:
		createStep = self.getStep( 'build-create-folders' )
		createStep.addMainAction( MkDirAction( self.getBaseDir() ) )
		# add action to delete the base directory (but not the log directory):
		cleanupStep = self.getStep( 'build-cleanup' )
		cleanupStep.prependMainAction( RmDirAction( self.getBaseDir() ) )
		# create the log directory
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode == Settings.RunMode_Build:
			try:
				os.makedirs( self.getLogDir() )
			except ( OSError, IOError )as e:
				raise ConfigurationError( 'Cannot create required log directory "{0}" for {1}: {2}!'
										.format( self.getLogDir(), self.getName(), e ) )
			try:
				os.makedirs( self.getPackagesDir() )
			except ( OSError, IOError )as e:
				raise ConfigurationError( 'Cannot create required packages directory "{0}" for {1}: {2}!'
					.format( self.getLogDir(), self.getName(), e ) )

	def calculateBuildSequence( self ):
		'''Define the build sequence for this object.
		By the default, the build sequence is identical for every BuildInstructions object. Command line parameters that
		enable or disable steps are applied by this method.'''
		buildSteps = self._setupBuildSteps( Settings.ProjectBuildSequence )
		# apply customizations passed as command line parameters:
		mApp().getParameters().applyBuildSequenceSwitches( buildSteps )
		return buildSteps

	def _executeStepRecursively( self, instructions, name ):
		'''Execute one step of the build sequence recursively, for this object, and all child objects.'''
		self.executeStep( name )
		for child in instructions.getChildren():
			child._executeStepRecursively( child, name )

	def executeStep( self, stepName ):
		'''Execute one individual step.
		This method does not recurse to child objects.'''
		step = self.getStep( stepName )
		if step.isEmpty():
			mApp().debugN( self, 4, 'step "{0}" is empty for {1}'.format( step.getName(), self.getName() ) )
			return
		mApp().debugN( self, 2, 'now executing step "{0}"'.format( step.getName() ) )
		if step.execute( self ):
			mApp().debugN( self, 1, 'success: "{0}"'.format( step.getName() ) )
		else:
			mApp().registerReturnCode( BuildError( 'dummy' ).getReturnCode() )
			mApp().debugN( self, 1, 'failure: "{0}"'.format( step.getName() ) )

