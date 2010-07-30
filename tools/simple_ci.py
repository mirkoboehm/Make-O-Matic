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
from core.MObject import MObject
import optparse
from core.Project import Project
from core.Settings import Settings
import sys
from core.Exceptions import ConfigurationError, MomError, MomException
import os
import time
from core.loggers.ConsoleLogger import ConsoleLogger
from buildcontrol.common.BuildStatus import BuildStatus
from buildcontrol.SubprocessHelpers import extend_debug_prefix, restore_debug_prefix

class SimpleCI( MObject ):
	"""SimpleCI implements a trivial Continuous Integration process that performs builds for a number of make-o-matic build scripts.
	"""

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.__project = Project( 'SimpleCI Process' )
		self.setControlDir( None )
		self.setPerformTestBuilds( False )
		self.setSlaveMode( False )
		self.setBuildScripts( None )
		self.setFindRevisions( True )
		self.setPerformBuilds( True )
		self.__buildStatus = BuildStatus()

	def getProject( self ):
		return self.__project

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
			self.getProject().debug( self, 'running in master mode' )
			# FIXME re-implement self-updating of the mom installation before calling the slave
			# ...
			# execute the build control process slave:
			cmd = '{0} {1}'.format( sys.executable, ' '.join( sys.argv + [ '--slave' ] ) )
			self.getProject().debug( self, '*** now starting slave CI process ***' )
			oldIndent = extend_debug_prefix( self.getProject(), 'slave' )
			result = -1
			try:
				result = os.system( cmd ) # do not use RunCommand, it catches the output
			finally:
				restore_debug_prefix( self.getProject(), oldIndent )
			self.getProject().debug( self, '*** slave finished with exit code {0}. ***'.format( result ) )
			if self.getPerformTestBuilds():
				break
			delay = 10 * 60
			if result != 0:
				# in case an error returned, we wait even longer, to not flood the server in case of a broken build script
				delay = 30 * 60
			self.getProject().debug( self, 'sleeping for {0} seconds.'.format( delay ) )
			self.getProject().debugN( self, 2, 'Z' )
			self.getProject().debugN( self, 2, 'z' )
			self.getProject().debugN( self, 2, '.' )
			time.sleep( delay )

	def beServant( self ):
		self.getProject().debug( self, 'running in slave mode' )
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
			exitCode = e.getReturnCode()
			self.getProject().message( self, 'error during slave run, exit code {0}: {1}'.format( exitCode, e ) )
			sys.exit( exitCode )
		self.getProject().debug( self, 'done, exiting.' )

	def performBuilds( self, buildScripts ):
		error = []
		# register all revisions committed since the last run in the database:
		if self.getFindRevisions():
			self.getProject().debug( self, 'build control: discovering new revisions' )
			for buildScript in buildScripts:
				try:
					self.getBuildStatus().registerNewRevisions( self.getProject(), buildScript )
				except MomError as e:
					error.append( 'error while processing build script "{0}": {1}'.format( buildScript, e ) )
					msg = 'error while processing build script "{0}", continuing: {1}'.format( buildScript, e )
					self.getProject().message( self, msg )
		else:
			self.getProject().debugN( self, 2, 'build control: skipping discovery of new revisions' )
		if self.getPerformBuilds():
			self.getProject().debug( self, 'build control: performing builds for new revisions' )
			# retrieve BuildInfo objects for all pending builds:
			buildInfos = self.getBuildStatus().listNewBuildInfos( self.getProject() )
			# perform the builds:
			for buildInfo in buildInfos:
				self.getBuildStatus().performBuild( self.getProject(), buildInfo )
		else:
			self.getProject().debugN( self, 2, 'build control: skipping build phase' )
		if error:
			raise MomError( '. '.join( error ) )

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
		( options, args ) = parser.parse_args( sys.argv )
		if options.control_dir:
			self.setControlDir( str( options.control_dir ) )
		if options.verbosity:
			level = int( options.verbosity )
			self.getProject().getSettings().set( Settings.ScriptLogLevel, level )
			self.getProject().debug( self, 'debug level is {0}'.format( level ) )
		if options.test_run:
			self.setPerformTestBuilds( True )
		if options.slaveMode:
			self.setSlaveMode( True )
		if options.no_find:
			self.setFindRevisions( False )
		if options.no_build:
			self.setPerformBuilds( False )
		self.setBuildScripts( args[1:] )

# "main":
# startup: get the current list of revisions, remember the highest one
# (current), and start compile jobs for every revision that comes in after
# that
# FIXME we should not exit in case a build script cannot be started, only remove this from the project list
# (easier self-repair)
try:
	ci = SimpleCI()
	# FIXME 
	ci.getBuildStatus().setDatabaseFilename( '/tmp/test-buildstatus.sqlite' )
	ci.getProject().addLogger( ConsoleLogger() )
	ci.parseParameters()
	if ci.getSlaveMode():
		ci.beServant()
	else:
		ci.beMaster()

except KeyboardInterrupt:
	print( 'Interrupted, exiting. Have a nice day.', file = sys.stderr )
	sys.exit( 1 )
except ConfigurationError as e:
	print( 'FATAL: A configuration error has been discovered. This means that a prerequisite of the build process is missing. '
		+ 'The following error message should explain the details:\n{0}'.format( str( e ) ) )
	sys.exit( 1 )
except MomError as e:
	print( 'FATAL: A MomError has been raised. This means there is a problem with the environment, system configuration or '
		+ 'make-o-matic itself that causes make-o-matic to malfunction. The following error message should explain the '
		+ 'details:\n{0}'.format( str( e ) ) )
	sys.exit( 1 )

