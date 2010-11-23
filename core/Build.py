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

import os
from core.MApplication import MApplication
from core.Project import Project
from core.Exceptions import ConfigurationError, MomError
from core.Settings import Settings
from core.Parameters import Parameters
from core.helpers.MachineInfo import machine_info
from core.helpers.GlobalMApp import mApp
import time
import shutil
import sys

class Build( MApplication ):
	'''Build represents the facilities provided by the currently running build script.
	It contains the loggers and reporters, for example. It also maintains the settings.'''

	def __init__( self, minimumMomVersion = None, name = None, parent = None ):
		MApplication.__init__( self, minimumMomVersion, name, parent )
		mApp().getSettings().set( Settings.ScriptBuildName, name )
		self.__project = None
		self.__parameters = Parameters()

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
		commands = {
			'revisions-since' : [ self.getProject().getScm().printRevisionsSince, 'print revisions committed since specified revision' ],
			'current-revision': [ self.getProject().getScm().printCurrentRevision, 'print current revision' ]
		}
		if command in commands:
			method = commands[ command ][0]
			print( method( options ) )
		else:
			text = 'Unknown command "{0}" for run mode "print". Known commands are:'.format( command )
			for cmd in commands:
				text += '\n   {0}: {1}'.format( cmd, commands[ cmd ][1] )
			raise ConfigurationError( text )

	def runPrepare( self ):
		'''Execute the prepare phase for builds.'''
		mApp().message( self, 'FIXME CHECK FOR SCM HERE' )
		# set folder names
		# the build object does not have a parent, and defines the build base dir:
		mode = self.getSettings().get( Settings.ScriptRunMode )
		if mode in ( Settings.RunMode_Build, Settings.RunMode_Describe ):
			parentBaseDir = os.getcwd()
			baseDirName = self._getBaseDirName()
			baseDir = os.path.join( parentBaseDir, baseDirName )
			self._setBaseDir( baseDir )
		else:
			self._setBaseDir( os.getcwd() )
		assert self.getBaseDir()
		return super( Build, self ).runPrepare()

	def runSetups( self ):
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
						shutil.rmtree( baseDir )
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
				os.makedirs( self._getLogDir() )
			except ( OSError, IOError )as e:
				raise ConfigurationError( 'Cannot create build log directory "{0}" for {1}: {2}!'
					.format( self._getLogDir(), self.getName(), e ) )
		super( Build, self ).runSetups()

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

	def runWrapups( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode == Settings.RunMode_Build:
			return MApplication.runWrapups( self )
		else:
			return None

	def runShutDowns( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode == Settings.RunMode_Build:
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

		return node
