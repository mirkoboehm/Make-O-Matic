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

from mom.apps.common.BuildScriptInterface import BuildScriptInterface
from mom.apps.common.BuildStatus import BuildStatus
from mom.apps.simple_ci.SimpleCiParameters import SimpleCiParameters
from mom.core.Exceptions import ConfigurationError, MomError
from mom.core.MApplication import MApplication
from mom.core.Settings import Settings
from mom.core.helpers.FilesystemAccess import make_foldername_from_string
from mom.core.helpers.GlobalMApp import mApp
from mom.core.loggers.ConsoleLogger import ConsoleLogger
import os

class SimpleCiBase( MApplication ):
	"""SimpleCI implements a trivial Continuous Integration process that performs builds for a number of Make-O-Matic build scripts.
	SimpleCIBase implements the common logic of the simple_ci master and slave processes.
	"""

	def __init__( self, name = None, parent = None ):
		MApplication.__init__( self, name, parent )

		self.__params = SimpleCiParameters()
		self.__params.parse()
		self.__buildStatus = BuildStatus()

	def preFlightCheck( self ):
		'''Perform the pre-flight check.'''
		self._setBaseDir( os.getcwd() )
		super( SimpleCiBase, self ).preFlightCheck()

	def getParameters( self ):
		'''Access the command line parameters.'''
		return self.__params

	def getBuildStatus( self ):
		'''Access the build status object.
		The BuildStatus object is the interface to the database of revisions and the build results.'''
		return self.__buildStatus

	def getToolName( self ):
		'''The tool name is used to select configuration files.'''
		raise NotImplementedError()

	def getInstanceName( self ):
		'''Instance name can be used if multiple independent SimpleCI instances are running on the same machine
		(since configuration files are usually loaded by host name).'''
		name = make_foldername_from_string( self.getName() )
		return name

	def getInstanceDir( self ):
		'''The instance directory contains all instance specific data.'''
		path = self.getSettings().getUserFolder( self.getToolName() )
		if not os.path.isdir( path ):
			try:
				os.makedirs( path )
				mApp().debug( self, 'instance directory "{0}" created.'.format( path ) )
			except OSError as e:
				raise ConfigurationError( 'cannot create instance directory "{0}": {1}!'.format( path, e ) )
		return path

	def getDataDir( self ):
		'''The data directory contains the build status database.'''
		path = os.path.join( self.getInstanceDir(), '{0}-data'.format( self.getInstanceName() ) )
		if not os.path.isdir( path ):
			try:
				os.makedirs( path )
				mApp().debug( self, 'instance data directory "{0}" created.'.format( path ) )
			except OSError as e:
				raise ConfigurationError( 'cannot create instance data directory "{0}": {1}!'.format( path, e ) )
		return path

	def build( self ):
		'''Execute the tool.'''
		settings = self.getSettings()
		settings.set( Settings.ScriptLogLevel, self.getParameters().getDebugLevel() )
		self.addLogger( ConsoleLogger() )
		# parse settings:
		settings.evalConfigurationFiles( self.getToolName() )
		settings.set( Settings.ScriptLogLevel, self.getParameters().getDebugLevel() )
		self.debug( self, 'debug level is {0}'.format( self.getParameters().getDebugLevel() ) )
		database = os.path.join( self.getDataDir(), 'buildstatus.sqlite' )
		self.debug( self, 'using database: {0}'.format( database ) )
		self.getBuildStatus().setDatabaseFilename( database )
		MApplication.build( self ) # call base class implementation

	def performBuilds( self, buildScripts ):
		'''PerformBuilds is the central method of a SimpleCI run.
		It retrieves new revisions, and calls the build scripts.'''
		error = []
		x = 0
		# register all revisions committed since the last run in the database:
		if self.getParameters().getFindRevisions():
			self.debug( self, 'build control: discovering new revisions' )
			for buildScript in buildScripts:
				try:
					self.getBuildStatus().registerNewRevisions( buildScript )
				except MomError as e:
					error.append( 'error while processing build script "{0}": {1}'.format( buildScript, e ) )
					msg = 'error while processing build script "{0}", continuing: {1}'.format( buildScript, e )
					self.message( self, msg )
		else:
			self.debugN( self, 2, 'build control: skipping discovery of new revisions' )
		if self.getParameters().getPerformBuilds():
			cap = self.getSettings().get( Settings.SimpleCIBuildJobCap )
			self.debug( self, 'build control: performing up to {0} builds for new revisions'.format( cap ) )
			self.getBuildStatus().listNewBuildInfos()
			for x in range( cap ):
				if not self.getBuildStatus().takeBuildInfoAndBuild( buildScripts ):
					break
			return x
		else:
			self.debugN( self, 2, 'build control: skipping build phase' )
		if error:
			raise MomError( '. '.join( error ) )
		return x

	def checkBuildScripts( self, buildScripts ):
		'''Verify that the build scripts are working as expected.
		The method checks that the build script can be called with basic parameters.
		@return all build scripts that passed the test
		'''
		buildNames = []
		goodScripts = []
		for buildScript in buildScripts:
			iface = BuildScriptInterface( buildScript )
			try:
				name = iface.querySetting( Settings.ScriptBuildName )
				if name and name not in buildNames:
					buildNames.append( name )
					goodScripts.append( buildScript )
				else:
					self.error( self, 'Error in build script "{0}": The build name "{1}" is already used by another '
								'build script. Build script disregarded.'.format( buildScript, name ) )
			except MomError, e:
				self.error( self, 'Error in build script "{0}": Error querying the build name. Build script disregarded. Reason: {1}'
					.format( buildScript, e ) )
		return goodScripts

	def runBuildScriptTestBuild( self, buildScripts ):
		'''Execute a test build for every build script.
		If enabled on the command line arguments, SimpleCI calls every build script once, and then exits.'''
		error = False
		caughtException = False
		for script in buildScripts:
			iface = BuildScriptInterface( script )
			name = iface.querySetting( Settings.ScriptBuildName )
			buildInfo = self.getBuildStatus().getBuildInfoForInitialRevision( script, name )
			buildInfo.setBuildType( 's' )
			try:
				if self.getBuildStatus().performBuild( buildInfo ):
					self.message( self, 'build script test run finished successfully for "{0}".'.format( script ) )
				else:
					self.message( self, 'build script test run finished with an error for "{0}".'.format( script ) )
					error = True
			except MomError:
				self.message( self, 'build script test run triggered an exception for "{0}"'.format( script ) )
				caughtException = True
		if caughtException:
			raise MomError( 'exception during build script test runs.' )
		elif error:
			self.registerReturnCode( 1 )
		else:
			pass

	def execute( self ):
		'''Execute needs to be implemented in the master and slave inherited classes.'''
		raise NotImplementedError()
