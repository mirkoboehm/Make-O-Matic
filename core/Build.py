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

from core.BuildParameters import BuildParameters
from core.Defaults import Defaults
from core.Exceptions import ConfigurationError, MomError
from core.MApplication import MApplication
from core.Parameters import Parameters
from core.Project import Project
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.helpers.MachineInfo import machine_info
from core.helpers.SafeDeleteTree import rmtree
from core.helpers.TimeUtils import formatted_time
from datetime import datetime
import os
import shutil
import sys
import time

class Build( MApplication ):
	'''Build represents the facilities provided by the currently running build script.
	It contains the loggers and reporters, for example. It also maintains the settings.'''

	def __init__( self, minimumMomVersion = None, name = None, parent = None ):
		MApplication.__init__( self, minimumMomVersion, name, parent )
		mApp().getSettings().set( Settings.ScriptBuildName, name )
		self.__project = None
		self.__parameters = BuildParameters()
		self.__startTime = datetime.utcnow()

	def getParameters( self ):
		return self.__parameters

	def initialize( self ):
		'''Determine the script run settings. 
		In the constructor, defaults will be applied. 
		First, the configuration files will be parsed.
		Second, the command line arguments will be applied. 
		On error, a subclass of MomException is thrown.
		Logging and reporting is not available at this stage yet.'''
		# first, parse configuration files:
		if os.getenv( "MOM_TESTS_RUNNING" ) == "1":
			self.debug( self, "Not loading configuration files, tests are running" )
		elif self.getParameters().getIgnoreConfigurationFiles():
			self.debug( self, "Not loading configuration files, requested per command switch" )
		else:
			self.getSettings().evalConfigurationFiles()

		# second, apply parameters:
		self.getParameters().apply( self.getSettings() )

	def setProject( self, project ):
		'''Every build has one master project. This method sets the master project.'''
		self.addProject( project )
		self.__project = project

	def getProject( self ):
		'''Return the master project for this build.'''
		return self.__project

	def addProject( self, project ):
		if not isinstance( project, Project ):
			raise ConfigurationError( 'The project variable needs to be an instance of the Project class!' )
		self.addChild( project )

	def _printSettings( self ):
		# program name, "print", argument, [options] 
		if len( self.getParameters().getArgs() ) < 3:
			raise MomError( 'Please specify parameter to print!' )
		command = self.getParameters().getArgs()[2]
		options = self.getParameters().getArgs()[3:]
		self.getProject().getScm()._handlePrintCommands( command, options )

	def prepare( self ):
		'''Execute the prepare phase for builds.'''
		super( Build, self ).prepare()
		# set folder names
		# the build object does not have a parent, and defines the build base dir:
		mode = self.getSettings().get( Settings.ScriptRunMode )
		if mode in ( Settings.RunMode_Build, Settings.RunMode_Describe ):
			# set base directory name
			parentBaseDir = os.getcwd()
			baseDirName = self._getBaseDirName()
			baseDir = os.path.join( parentBaseDir, baseDirName )
			self._setBaseDir( baseDir )
			# set the base log directory name
			logDirName = mApp().getSettings().get( Defaults.ProjectLogDir )
			logDir = os.path.join( baseDir, logDirName )
			self.setLogDir( logDir )
			# set the base packages directory name
			packagesDirName = mApp().getSettings().get( Defaults.ProjectPackagesDir )
			packagesDir = os.path.join( baseDir, packagesDirName )
			self.setPackagesDir( packagesDir )
		else:
			self._setBaseDir( os.getcwd() )
			self.setLogDir( os.getcwd() )
			self.setPackagesDir( os.getcwd() )
		assert self.getBaseDir()
		for step in self.calculateBuildSequence():
			self.addStep( step )


	def setup( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode == Settings.RunMode_Build:
			baseDir = self.getBaseDir()
			if os.path.isdir( baseDir ):
				moveOldDirectories = mApp().getSettings().get( Settings.BuildMoveOldDirectories )
				if moveOldDirectories:
					mApp().debug( self, 'stale base directory exists, moving it.' )
					stats = os.stat( baseDir )
					mtime = time.localtime( stats[8] )
					extension = time.strftime( "%Y-%m-%d-%H-%M-%S", mtime )
					newFolderBaseName = '{0}-{1}'.format( baseDir, extension )
					newFolder = newFolderBaseName
					maxIterations = 1000
					for index in range( maxIterations ):
						if not os.path.isdir( newFolder ):
							break
						newFolder = newFolderBaseName + '__{0}'.format( index + 1 )
					if os.path.isdir( newFolder ):
						raise MomError( "{0} old build directories exist, this can't be happening :-(".format( maxIterations ) )
					try:
						shutil.move( baseDir, newFolder )
					except ( OSError, shutil.Error ) as o:
						raise ConfigurationError( 'Cannot move existing build folder at "{0}" to "{1}": {2}'
							.format( baseDir, newFolder, str( o ) ) )
					mApp().debugN( self, 2, 'moved to "{0}".'.format( newFolder ) )
				else:
					try:
						rmtree( baseDir )
					except ( OSError, shutil.Error ) as o:
						raise ConfigurationError( 'Cannot remove existing build folder at "{0}": {1}'
							.format( baseDir, str( o ) ) )
			try:
				os.makedirs( baseDir )
			except ( OSError, IOError ) as e:
				raise ConfigurationError( 'Cannot create required base directory "{0}" for {1}: {2}!'
										.format( baseDir, self.getName(), e ) )
			os.chdir( baseDir )
			try:
				os.makedirs( self.getLogDir() )
			except ( OSError, IOError )as e:
				raise ConfigurationError( 'Cannot create build log directory "{0}" for {1}: {2}!'
					.format( self.getLogDir(), self.getName(), e ) )
			try:
				os.makedirs( self.getPackagesDir() )
			except ( OSError, IOError )as e:
				raise ConfigurationError( 'Cannot create build packages directory "{0}" for {1}: {2}!'
					.format( self.getLogDir(), self.getName(), e ) )
		super( Build, self ).setup()

	def runPreFlightChecks( self ):
		if self.getSettings().get( Settings.ScriptRunMode ) in ( Settings.RunMode_Query, Settings.RunMode_Print ):
			return # no pre-flight check in query and print modes, do nothing

		super( Build, self ).runPreFlightChecks() # run base class' implementation

	def runExecute( self ):
		if self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Describe:
			self.describeRecursively()
			sys.stdout.flush() # required, do not remove
		elif self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Build:
			return super( Build, self ).runExecute()
		elif self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Query:
			self._queryAndPrintSettings( self.getParameters().getArgs()[2:] )
		elif self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Print:
			self._printSettings()
		else:
			pass
		return None

	def execute( self ):
		with self.getTimeKeeper():
			self.executeSteps()
			super( Build, self ).execute()

	def executeSteps( self ):
		for step in self.getSteps():
			self._executeStepRecursively( self, step.getName() )

	def runWrapups( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode == Settings.RunMode_Build:
			return MApplication.runWrapups( self )
		else:
			return None

	def runReports( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode != Settings.RunMode_Build:
			return

		MApplication.runReports( self )

	def runNotifications( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode != Settings.RunMode_Build:
			return

		MApplication.runNotifications( self )

	def runShutDowns( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode == Settings.RunMode_Build and not self.getParameters().getDisableShutdown():
			if self.getDeleteLogDirOnShutdown():
				try:
					if os.path.isdir( self.getLogDir() ):
						mApp().debugN( self, 2, 'deleting log directory structure at "{0}"'.format( self.getLogDir() ) )
						shutil.rmtree( self.getLogDir() )
				except OSError as e:
					raise ConfigurationError( 'Cannot delete log directory at "{0}": {1}'.format( self.getLogDir(), str( e ) ) )
			if self.getPackagesDir():
				try:
					if os.path.isdir( self.getPackagesDir() ):
						mApp().debugN( self, 2, 'deleting packages directory structure at "{0}"'.format( self.getPackagesDir() ) )
						shutil.rmtree( self.getPackagesDir() )
				except OSError as e:
					raise ConfigurationError( 'Cannot delete packages directory at "{0}": {1}'.format( self.getPackagesDir(),
						str( e ) ) )
			return MApplication.runShutDowns( self )
		else:
			return None

	def _buildAndReturn( self ):
		'''Overloaded method that verifies the run mode.'''
		if self.getSettings().get( Settings.ScriptRunMode ) not in  Settings.RunModes:
			raise MomError( 'Unknown run mode "{0}". Known run modes are: {1}'.format( 
					self.getSettings().get( Settings.ScriptRunMode ),
					', '.join( Settings.RunModes ) ) )
		return MApplication._buildAndReturn( self )

	def createXmlNode( self, document, recursive = True ):
		node = MApplication.createXmlNode( self, document, recursive )

		# add machine info
		for key, value  in machine_info().items():
			node.attributes[key] = value

		node.attributes["returncode"] = str( self.getReturnCode() )
		node.attributes["startTime"] = str ( formatted_time( self.__startTime ) )
		node.attributes["sys-shortname"] = self.getSystemShortName()

		return node
