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
from core.Exceptions import ConfigurationError, MomError
import os
import time
from core.loggers.ConsoleLogger import ConsoleLogger
from core.helpers.RunCommand import RunCommand
from buildcontrol.common.BuildInfo import BuildInfo
from buildcontrol.common.BuildStatus import BuildStatus
import re

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
		self.setBuildType( None )
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

	def setBuildType( self, type ):
		self.__buildType = type

	def getBuildType( self ):
		return self.__buildType

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
			# FIXME re-implement self-updating of the mom installation before calling the slave
			# ...
			# execute the build control process slave:
			cmd = '{0} {1}'.format( sys.executable, ' '.join( sys.argv + [ '--slave' ] ) )
			self.getProject().debugN( self, 3, '*** now starting slave build control process ***' )
			# FIXME load from settings:
			indentVar = 'MOM_INTERNAL_DEBUG_INDENT'
			oldIndent = ''
			if indentVar in os.environ:
				oldIndent = os.environ[ indentVar ] + ' '
			os.environ[ indentVar ] = '{0}slave> '.format( oldIndent )
			result = os.system( cmd ) # do not use runcommand, it catches the output
			os.environ[ indentVar ] = oldIndent
			if self.getPerformTestBuilds():
				break
			if result == 0:
				time.sleep( 10 * 60 )
			else:
				text = '*** slave build control process failed with return code {0}, better check it while I sleep ***'\
					.format( str( result ) )
				self.getProject().debug( self, text )
				# in case an error returned, we wait even longer, to not flood the server in case of a broken build script
				time.sleep( 30 * 60 )

	def beServant( self ):
		self.getProject().debug( self, 'running in slave mode' )
		# we are now in slave mode
		# branch by build type:
		buildType = 'c'
		if self.getBuildType():
			buildType = str( self.getBuildType() ).lower()
			knownBuildTypes = 'cd'
			if buildType not in knownBuildTypes:
				raise ConfigurationError( 'I don\'t know about {0} type builds. Known build types are {1}.'
					.format( buildType.upper(), ', '.join( knownBuildTypes ) ) )
			self.getProject().message( self, 'will do {0} type builds.'.format( buildType.upper() ) )
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
		if self.getPerformTestBuilds():
			self.getProject().message( self, 'will do a test build for every product' )
			# FIXME Mirko
			# runTestBuildJobs( Options, folderScripts )
		elif buildType == 'c':
			self.doContinuousBuilds( buildScripts )
		elif buildType == 'd':
			# FIXME Mirko
			pass
			# doDailyBuilds( Options, RunDir, folderScripts )
		else:
			raise MomError( 'simple_ci only knows about C and D builds!' )
		self.getProject().debugN( self, 1, 'done, exiting.' )

	def querySetting( self, buildScript, setting ):
		cmd = '{0} {1} query {2}'.format( sys.executable, buildScript, setting )
		runner = RunCommand( self.getProject(), cmd, 1800 )
		runner.run()
		if runner.getReturnCode() != 0:
			stderr = runner.getStdErr().decode()
			raise MomError( 'Cannot query project name for build script "{0}"!'.format( stderr ) )
		output = runner.getStdOut()
		if not output:
			raise MomError( 'The build script "{0}" did not specify a project name!'.format( stderr ) )
		line = output.decode().strip()
		groups = re.search( '^(.+?): (.+)$', line )
		if not groups:
			raise MomError( 'Did not understand this output: "{0}"!'.format( line ) )
		variable = groups.groups()[1]
		return variable


	def doContinuousBuilds( self, buildScripts ):
		self.getProject().debug( self, 'build control: running in continuous build mode' )
		buildInfos = []
		for buildScript in buildScripts:
			projectName = self.querySetting( buildScript, Settings.ProjectName )
			newestBuildInfo = self.getBuildStatus().getNewestBuildInfo( buildScript )
			if newestBuildInfo:
				self.getProject().debugN( self, 2, 'newest known revision for build script "{0}" ({1}) is "{2}"'
					.format( buildScript, projectName, newestBuildInfo.getRevision() ) )
				cmd = '{0} {1} print revisions-since {2}'.format( sys.executable, buildScript, newestBuildInfo.getRevision() )
				runner = RunCommand( self.getProject(), cmd, 1800 )
				runner.run()
				if runner.getReturnCode() != 0:
					msg = 'Cannot get revision list for build script "{0}" ({1}), continuing with next project.'\
						.format( buildScript, projectName )
					self.getProject().message( msg )
					continue
				output = runner.getStdOut()
				if not output: continue
				lines = output.decode().split( '\n' )
				for line in lines:
					line = line.strip()
					if not line: continue
					parts = line.split( ' ' )
					if len( parts ) != 3:
						self.getProject().message( self, 'Not understood, skipping: "{0}"'.format( line ) )
						continue
					buildInfo = BuildInfo()
					buildInfo.setProjectName( projectName )
					buildInfo.setBuildStatus( buildInfo.Status.NewRevision )
					buildInfo.setBuildType( parts[0] )
					buildInfo.setRevision( parts[1] )
					buildInfo.setUrl( parts[2] )
					buildInfo.setBuildScript( buildScript )
					buildInfos.append( buildInfo )
			#	 persist all newly discovered revisions:
				buildInfos.reverse()
				self.getBuildStatus().saveBuildInfo( buildInfos )
			else:
				cmd = '{0} {1} print current-revision'.format( sys.executable, buildScript )
				runner = RunCommand( self.getProject(), cmd, 1800 )
				runner.run()
				if runner.getReturnCode() != 0:
					msg = 'Cannot get initial revision for build script "{0}" ({1}), continuing with next project.'\
						.format( buildScript, projectName )
					self.getProject().message( msg )
					continue
				revision = runner.getStdOut().decode().strip()
				buildInfo = BuildInfo()
				buildInfo.setProjectName( projectName )
				buildInfo.setBuildStatus( buildInfo.Status.InitialRevision )
				buildInfo.setRevision( revision )
				buildInfo.setBuildScript( buildScript )
				buildInfos.append( buildInfo )
				self.getProject().debug( self, 'saving initial revision "{0}" for build script "{1}" ({2})'
					.format( revision, buildScript, projectName ) )
				self.getBuildStatus().saveBuildInfo( [ buildInfo ] )

	def parseParameters ( self ):
		"""Parse command line options, give help"""
		parser = optparse.OptionParser()
		parser.add_option( "-c", "--control-folder", type = "string", dest = "control_dir",
			help = "select control folder that contains the build scripts" )
		parser.add_option( '-v', '--verbose', action = 'count', dest = 'verbosity',
			help = 'level of debug output' )
		parser.add_option( "-d", "--test-run", action = "store_true", dest = "test_run",
			help = "compile the last revision of every product for testing" )
		parser.add_option( "-t", "--build-type", type = "string", dest = "build_type",
			help = "build type, known types are (C)ontinuous and (D)aily" )
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
		if options.build_type:
			self.setBuildType( options.build_type )
		if options.slaveMode:
			self.setSlaveMode( True )
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
	print( """\
FATAL: A configuration error has been discovered. This means that a pre-
requisite of the build process is missing. The following error message
should explain the details:\n{0}""".format( str( e ) ) )
	sys.exit( 1 )
except MomError as e:
	print( """\
FATAL: A MomError has been raised. This means there is a problem
with the environment, system configuration or make-o-matic itself that
causes make-o-matic to malfunction. The following error message should 
explain the details:\n{0}""".format( str( e ) ) )
	sys.exit( 1 )

