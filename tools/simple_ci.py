#!/usr/bin/env python3

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
from core.MApplication import MApplication
from buildcontrol.common.BuildStatus import BuildStatus
from core.helpers.FilesystemAccess import make_foldername_from_string
import os
from core.Exceptions import ConfigurationError, MomError, MomException
from core.Settings import Settings
from core.loggers.ConsoleLogger import ConsoleLogger
import optparse
import sys
from buildcontrol.SubprocessHelpers import extend_debug_prefix, restore_debug_prefix
import time
from buildcontrol.common.BuildScriptInterface import BuildScriptInterface
from core.helpers.GlobalMApp import mApp

class SimpleCI( MApplication ):
	"""SimpleCI implements a trivial Continuous Integration process that performs builds for a number of make-o-matic build scripts.
	"""

	def __init__( self, name = None, parent = None ):
		MApplication.__init__( self, name, parent )
		self.__setDebugLevelParameter( 0 )
		self.setControlDir( None )
		self.setPerformTestBuilds( False )
		self.setDelay( None )
		self.setSlaveMode( False )
		self.setBuildScripts( None )
		self.setFindRevisions( True )
		self.setPerformBuilds( True )
		self.__buildStatus = BuildStatus()

	def getBuildStatus( self ):
		return self.__buildStatus

	def setControlDir( self, dir ):
		self.__controlDir = dir

	def getControlDir( self ):
		return self.__controlDir

	def setPerformTestBuilds( self, doIt ):
		self.__performTestBuilds = doIt

	def getPerformTestBuilds( self ):
		return self.__performTestBuilds

	def setDelay( self, delay ):
		self.__delay = delay

	def getDelay( self ):
		return self.__delay

	def setSlaveMode( self, onoff ):
		self.__slaveMode = onoff

	def getSlaveMode( self ):
		return self.__slaveMode

	def setBuildScripts( self, scripts ):
		self.__buildScripts = scripts

	def getBuildScripts( self ):
		return self.__buildScripts

	def setFindRevisions( self, doIt ):
		self.__find = doIt

	def getFindRevisions( self ):
		return self.__find

	def setPerformBuilds( self, doIt ):
		self.__build = doIt

	def getPerformBuilds( self ):
		return self.__build

	def __setDebugLevelParameter( self, level ):
		self.__debugLevelParameter = level

	def __getDebugLevelParameter( self ):
		return self.__debugLevelParameter

	def getToolName( self ):
		name = make_foldername_from_string( self.__class__.__name__ )
		return name

	def getInstanceName( self ):
		name = make_foldername_from_string( self.getName() )
		return name

	def getInstanceDir( self ):
		folder = make_foldername_from_string( self.getToolName() )
		# FIXME verify on Windows
		path = os.path.join( os.path.expanduser( '~' ), '.mom', folder )
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

	def parseParameters ( self ):
		"""Parse command line options, give help"""
		parser = optparse.OptionParser()
		parser.add_option( "-c", "--control-folder", type = "string", dest = "control_dir",
			help = "select control folder that contains the build scripts" )
		parser.add_option( '-v', '--verbose', action = 'count', dest = 'verbosity',
			help = 'level of debug output' )
		parser.add_option( "-d", "--test-run", action = "store_true", dest = "test_run",
			help = "compile the last revision of every product for testing" )
		parser.add_option( "-f" , "--no-find", action = "store_true", dest = "no_find",
			help = "do not try to discover new revisions for the projects (default: do try)" )
		parser.add_option( "-b", "--no-build", action = "store_true", dest = "no_build",
			help = "do not start build jobs for new revisions (default: do build)" )
		parser.add_option( "-s", "--slave", action = "store_true", dest = "slaveMode",
			help = "run in slave mode (the one that actually does the builds)" )
		parser.add_option( "-n", "--instance-name", type = "string", dest = "instance_name",
			help = "the instance name is used to locate the configuration and database files (see debug output)" )
		parser.add_option( '-p', '--pause', type = 'int', dest = 'delay',
			help = 'pause after every slave run, in seconds' )
		( options, args ) = parser.parse_args( sys.argv )
		if options.control_dir:
			self.setControlDir( str( options.control_dir ) )
		if options.verbosity:
			level = int( options.verbosity )
			self.__setDebugLevelParameter( level )
		if options.test_run:
			self.setPerformTestBuilds( True )
		if options.slaveMode:
			self.setSlaveMode( True )
		if options.no_find:
			self.setFindRevisions( False )
		if options.no_build:
			self.setPerformBuilds( False )
		if options.delay:
			self.setDelay( options.delay )
		if options.instance_name:
			self.setName( options.instance_name )
		self.setBuildScripts( args[1:] )

	def beMaster( self ):
		"""This is the main driver method when the control process is run as the master.
		In an endless loop, it invokes itself in slave mode to perform all builds that have accumulated since the last start.
		After every run, the master takes a short sleep."""
		print( """\
+-+-+-+-+-+-+-+-+-+-+-+-+                     +-+ +-+-+-+-+ +-+-+-+-+
|m|a|k|e|-|o|-|m|a|t|i|c|                     |C| |K|D|A|B| |2|0|1|0|
+-+-+-+-+-+-+-+-+-+-+-+-+                     +-+ +-+-+-+-+ +-+-+-+-+
+-+ +-+-+-+-+-+ +-+ +-+-+-+-+-+ +-+-+-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
|i| |m|4|k|e|s| |u| |n|o|o|b|s| |k|n|o|w| |w|4|z|z| |f|0|0|b|4|r|3|d|
+-+ +-+-+-+-+-+ +-+ +-+-+-+-+-+ +-+-+-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
""" )
		while True:
			self.debug( self, 'running in master mode' )
			# FIXME re-implement self-updating of the mom installation before calling the slave
			# ...
			# execute the build control process slave:
			cmd = '{0} {1}'.format( sys.executable, ' '.join( sys.argv + [ '--slave' ] ) )
			self.debug( self, '*** now starting slave CI process ***' )
			oldIndent = extend_debug_prefix( 'slave' )
			result = -1
			try:
				result = os.system( cmd ) # do not use RunCommand, it catches the output
			finally:
				restore_debug_prefix( oldIndent )
			self.debug( self, '*** slave finished with exit code {0}. ***'.format( result ) )
			if self.getPerformTestBuilds():
				break
			period = 5
			self.debug( self, 'short break of {0} seconds'.format( period ) )
			time.sleep( period )

	def beServant( self ):
		self.debug( self, 'running in slave mode' )
		# we are now in slave mode
		# find the build scripts
		buildScripts = self.getBuildScripts() or []
		if self.getControlDir():
			BaseDir = str( self.getControlDir() )
			mApp().message( self, 'using "{0}" as control directory.'.format( BaseDir ) )
			ControlDir = os.path.normpath( os.path.join( os.getcwd(), BaseDir ) )
			if not os.path.isdir( ControlDir ):
				raise ConfigurationError( 'The control directory "{0}" does not exist!'.format( ControlDir ) )
			folderScripts = filter( lambda x: x.endswith( '.py' ), os.listdir( ControlDir ) )
			folderScripts = map( lambda x: ControlDir + os.sep + x, folderScripts )
			folderScripts = map( lambda x: os.path.normpath( x ), folderScripts )
			buildScripts += folderScripts
		if not buildScripts:
			mApp().message( self, 'FYI: no build scripts specified.' )
		buildScripts = self.checkBuildScripts( buildScripts )
		# do the stuff
		sleepPeriod = 5 * 60 # if there was nothing to do, wait a little before retrying, to not hog the remote side
		try:
			if self.getPerformTestBuilds():
				sleepPeriod = 0
				self.message( self, 'will do a test build for the latest revision of every build script' )
				self.runBuildScriptTestBuild( buildScripts )
			else:
				count = self.performBuilds( buildScripts )
				if count:
					sleepPeriod = 5 # just to avoid spawn races in case there is some problem
		except MomException as e:
			self.registerReturnCode( e.getReturnCode() )
			self.message( self, 'error during slave run, exit code {0}: {1}'.format( 
				self.getReturnCode(), e ) )
			sleepPeriod = 15 * 60 # if there is a problem, the process interrupts for a little longer, to allow for it to be fixed
		finally:
			if self.getDelay():
				sleepPeriod = self.getDelay()
			if sleepPeriod:
				self.debug( self, 'sleeping for {0} seconds.'.format( sleepPeriod ) )
				self.debugN( self, 2, 'Z' )
				self.debugN( self, 2, 'z' )
				self.debugN( self, 2, '.' )
				time.sleep( sleepPeriod )
			self.debug( self, 'done, exiting.' )

	def performBuilds( self, buildScripts ):
		error = []
		x = 0
		# register all revisions committed since the last run in the database:
		if self.getFindRevisions():
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
		if self.getPerformBuilds():
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
				name = iface.querySetting( Settings.ProjectName )
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
			name = iface.querySetting( Settings.ProjectName )
			buildInfo = self.getBuildStatus().getBuildInfoForInitialRevision( script, name )
			buildInfo.setBuildType( 's' )
			try:
				if self.getBuildStatus().performBuild( buildInfo ):
					self.message( self, 'build script test run finished successfully for "{0}".'.format( script ) )
				else:
					self.message( self, 'build script test run finished with an error for "{0}".'.format( script ) )
					error = True
			except MomError:
				self.message( 'self, build script test run triggered an exception for "{0}"'.format( script ) )
				caughtException = True
		if caughtException:
			raise MomError( 'exception during build script test runs.' )
		elif error:
			self.registerReturnCode( 1 )
		else:
			pass

	def execute( self ):
		if self.getSlaveMode():
			self.beServant()
		else:
			self.beMaster()

	def build( self ):
		self.parseParameters()
		settings = self.getSettings()
		settings.set( Settings.ScriptLogLevel, self.__getDebugLevelParameter() )
		self.addLogger( ConsoleLogger() )
		# parse settings:
		settings.evalConfigurationFiles( self.getToolName() )
		settings.set( Settings.ScriptLogLevel, self.__getDebugLevelParameter() )
		self.debug( self, 'debug level is {0}'.format( self.__getDebugLevelParameter() ) )
		# set database filename:
		database = os.path.join( self.getDataDir(), 'buildstatus.sqlite' )
		self.getBuildStatus().setDatabaseFilename( database )
		MApplication.build( self ) # call base class implementation


if __name__ == "__main__":
	ci = SimpleCI()
	ci.build()
