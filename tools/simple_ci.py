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

class SimpleCI( MApplication ):
	"""SimpleCI implements a trivial Continuous Integration process that performs builds for a number of make-o-matic build scripts.
	"""

	def __init__( self, name = None ):
		MApplication.__init__( self, name )
		self.__setDebugLevelParameter( 0 )
		self.setControlDir( None )
		self.setPerformTestBuilds( False )
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
				self.getProject().debug( self, 'instance directory "{0}" created.'.format( path ) )
			except OSError as e:
				raise ConfigurationError( 'cannot create instance directory "{0}": {1}!'.format( path, e ) )
		return path

	def getDataDir( self ):
		path = os.path.join( self.getInstanceDir(), '{0}-data'.format( self.getInstanceName() ) )
		if not os.path.isdir( path ):
			try:
				os.makedirs( path )
				self.getProject().debug( self, 'instance data directory "{0}" created.'.format( path ) )
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
		if options.instance_name:
			self.setName( options.instance_name )
		self.setBuildScripts( args[1:] )

	def beServant( self ):
		self.debug( self, 'running in slave mode' )
		# we are now in slave mode
		# find the build scripts
		buildScripts = self.getBuildScripts() or []
		if self.getControlDir():
			BaseDir = str( self.getControlDir() )
			self.getProject().message( self, 'using "{0}" as control directory.'.format( BaseDir ) )
			ControlDir = os.path.normpath( os.path.join( os.getcwd(), BaseDir ) )
			if not os.path.isdir( ControlDir ):
				raise ConfigurationError( 'The control directory "{0}" does not exist!'.format( ControlDir ) )
			folderScripts = filter( lambda x: x.endswith( '.py' ), os.listdir( ControlDir ) )
			folderScripts = map( lambda x: ControlDir + os.sep + x, folderScripts )
			folderScripts = map( lambda x: os.path.normpath( x ), folderScripts )
			buildScripts += folderScripts
		if not buildScripts:
			self.getProject().message( self, 'FYI: no build scripts specified.' )
		# FIXME Mirko
		# buildScripts = BuildControl.DoSanityChecks( BaseDir, buildScripts, buildType )
		# do the stuff
		try:
			if self.getPerformTestBuilds():
				self.getProject().message( self, 'will do a test build for every product' )
				raise MomError( 'Not implemented: text builds mode!' )
				# FIXME Mirko
				# runTestBuildJobs( Options, folderScripts )
			else:
				self.performBuilds( buildScripts )
		except MomException as e:
			self.registerReturnCode( e.getReturnCode() )
			self.message( self, 'error during slave run, exit code {0}: {1}'.format( 
				self.getReturnCode(), e ) )
			self.debug( self, 'done, exiting.' )

	def performBuilds( self, buildScripts ):
		error = []
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
				x = x
				if not self.getBuildStatus().takeBuildInfoAndBuild():
					break
		else:
			self.debugN( self, 2, 'build control: skipping build phase' )
		if error:
			raise MomError( '. '.join( error ) )

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
