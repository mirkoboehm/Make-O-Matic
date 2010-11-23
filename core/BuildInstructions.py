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
from core.helpers.TypeCheckers import check_for_path_or_none, check_for_nonempty_string
from core.executomat.Step import Step
from core.actions.filesystem.MkDirAction import MkDirAction
from core.actions.filesystem.RmDirAction import RmDirAction

class BuildInstructions( Instructions ):
	def __init__( self, name = None, parent = None ):
		Instructions.__init__( self, name, parent )
		self.__steps = []
		self.__timeKeeper = TimeKeeper()
		self.setLogDir( None )
		self.__failedStep = None

	def hasFailed( self ):
		return self.__failedStep != None

	def logFilePathForFailedStep( self ):
		if self.__failedStep:
			return self.__failedStep.getLogFileName()

	def setLogDir( self, path ):
		"""Set the directory where all log information is stored."""
		check_for_path_or_none( path, "The log directory name must be a string containing a path name." )
		self.__logDir = path

	# FIXME bad name, Project has getLogDir, this is confusing
	def _getLogDir( self ):
		"""Return the log dir."""
		return self.__logDir

	def addStep( self, newStep ):
		"""Add a newStep identified by identifier. If the identifier already exists, the new 
		command replaces the old one."""
		if not isinstance( newStep, Step ):
			raise MomError( 'only executomat.Step instances can be added to the queue' )
		check_for_nonempty_string( newStep.getName(), "Every Executomat step must have a name!" )
		self.__steps.append( newStep )

	def getSteps( self ):
		return self.__steps

	def getStep( self, identifier ):
		"""Find the step with this identifier and return it."""
		for step in self.getSteps():
			if step.getName() == identifier:
				return step
		raise MomError( 'no such step "{0}"'.format( identifier ) )

	def getTimeKeeper( self ):
		return self.__timeKeeper

	def describe( self, prefix ):
		Instructions.describe( self, prefix )
		for step in self.getSteps():
			step.describe( prefix + '    ' )

	def createXmlNode( self, document ):
		node = Instructions.createXmlNode( self, document )
		node.attributes["starttime"] = str ( formatted_time( self.getTimeKeeper().getStartTime() ) )
		node.attributes["stoptime"] = str ( formatted_time( self.getTimeKeeper().getStopTime() ) )
		node.attributes["timing"] = str( self.getTimeKeeper().deltaString() )

		stepsElement = document.createElement( "steps" )
		for step in self.getSteps():
			element = step.createXmlNode( document )
			stepsElement.appendChild( element )
		node.appendChild( stepsElement )

		return node

	def runPrepare( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode in ( Settings.RunMode_Build, Settings.RunMode_Describe ):
			# set base dir
			parentBaseDir = self.getParent().getBaseDir()
			baseDirName = self._getBaseDirName()
			baseDir = os.path.join( parentBaseDir, baseDirName )
			self._setBaseDir( baseDir )
			# set log dir
			logDirName = self._getBaseDirName()
			parentLogDir = self.getParent()._getLogDir()
			logDir = os.path.abspath( os.path.join( parentLogDir, logDirName ) )
			self.setLogDir( logDir )
		else:
			self._setBaseDir( os.getcwd() )
			self._setLogDir( os.getcwd() )
		return super( BuildInstructions, self ).runPrepare()

	def runSetups( self ):
		for step in self.calculateBuildSequence():
			self.addStep( step )
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
				os.makedirs( self._getLogDir() )
			except ( OSError, IOError )as e:
				raise ConfigurationError( 'Cannot create required log directory "{0}" for {1}: {2}!'
										.format( self._getLogDir(), self.getName(), e ) )
		super( BuildInstructions, self ).runSetups()

	def calculateBuildSequence( self ):
		buildSteps = self._setupBuildSteps( Settings.ProjectBuildSequence )
		# apply customizations passed as command line parameters:
		mApp().getParameters().applyBuildSequenceSwitches( buildSteps )
		return buildSteps

	def _executeStepRecursively( self, instructions, name ):
		self.executeStep( name )
		for child in instructions.getChildren():
			child._executeStepRecursively( child, name )

	def executeStep( self, stepName ):
		step = self.getStep( stepName )
		if step.isEmpty():
			mApp().debugN( self, 4, 'step "{0}" is empty for {1}'.format( step.getName(), self.getName() ) )
			return
		mApp().debugN( self, 2, 'now executing step "{0}"'.format( step.getName() ) )
		if step.execute( self ):
			mApp().debugN( self, 1, 'success: "{0}"'.format( step.getName() ) )
		else:
			if self.__failedStep == None:
				# we are only interested in the log files for the first failure 
				self.__failedStep = step
			mApp().registerReturnCode( BuildError( 'dummy' ).getReturnCode() )
			mApp().debugN( self, 1, 'failure: "{0}"'.format( step.getName() ) )
