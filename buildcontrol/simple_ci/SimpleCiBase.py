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
from core.MApplication import MApplication
from buildcontrol.common.BuildStatus import BuildStatus
from core.helpers.FilesystemAccess import make_foldername_from_string
import os
from core.Exceptions import ConfigurationError, MomError
from core.Settings import Settings
from core.loggers.ConsoleLogger import ConsoleLogger
from core.helpers.GlobalMApp import mApp
from buildcontrol.common.BuildScriptInterface import BuildScriptInterface

class SimpleCiBase( MApplication ):
	"""SimpleCI implements a trivial Continuous Integration process that performs builds for a number of make-o-matic build scripts.
	"""

	def __init__( self, params, name = None, parent = None ):
		MApplication.__init__( self, name, parent )
		self.__params = params
		self.__buildStatus = BuildStatus()

	def runPreFlightChecks( self ):
		self._setBaseDir( os.getcwd() )
		MApplication.runPreFlightChecks( self )

	def getParameters( self ):
		return self.__params

	def getBuildStatus( self ):
		return self.__buildStatus

	def getToolName( self ):
		raise NotImplementedError()

	def getInstanceName( self ):
		name = make_foldername_from_string( self.getName() )
		return name

	def getInstanceDir( self ):
		path = self.getSettings().userFolder( self.getToolName() )
		if not os.path.isdir( path ):
			try:
				os.makedirs( path )
				mApp().debug( self, 'instance directory "{0}" created.'.format( path ) )
			except OSError as e:
				raise ConfigurationError( 'cannot create instance directory "{0}": {1}!'.format( path, e ) )
		return path

	def getDataDir( self ):
		path = os.path.join( self.getInstanceDir(), '{0}-data'.format( self.getInstanceName() ) )
		if not os.path.isdir( path ):
			try:
				os.makedirs( path )
				mApp().debug( self, 'instance data directory "{0}" created.'.format( path ) )
			except OSError as e:
				raise ConfigurationError( 'cannot create instance data directory "{0}": {1}!'.format( path, e ) )
		return path

	def build( self ):
		settings = self.getSettings()
		settings.set( Settings.ScriptLogLevel, self.getParameters().getDebugLevel() )
		self.addLogger( ConsoleLogger() )
		# parse settings:
		settings.evalConfigurationFiles( self.getToolName() )
		settings.set( Settings.ScriptLogLevel, self.getParameters().getDebugLevel() )
		self.debug( self, 'debug level is {0}'.format( self.getParameters().getDebugLevel() ) )
		database = os.path.join( self.getDataDir(), 'buildstatus.sqlite' )
		self.getBuildStatus().setDatabaseFilename( database )
		MApplication.build( self ) # call base class implementation

	def performBuilds( self, buildScripts ):
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
		goodScripts = []
		for buildScript in buildScripts:
			iface = BuildScriptInterface( buildScript )
			try:
				name = iface.querySetting( Settings.ScriptBuildName )
				if name:
					goodScripts.append( buildScript )
			except MomError:
				self.message( self, 'ERROR in build script "{0}": error querying the project name. Build script disregarded.'
					.format( buildScript ) )
		return goodScripts

	def runBuildScriptTestBuild( self, buildScripts ):
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
		raise NotImplementedError()
