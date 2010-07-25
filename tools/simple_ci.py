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

	def getProject( self ):
		return self.__project

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

	def beMaster( self ):
		pass

	def beServant( self ):
		return
#		DebugN( 1, 'running in slave mode' )
#		# we are now in slave mode
#		# branch by build type:
#		buildType = 'c'
#		if Options.build_type:
#			buildType = str( Options.build_type ).lower()
#			KnownBuildTypes = 'CD'
#			if buildType.upper() not in KnownBuildTypes:
#				raise ConfigureError( "I don't know about \"" + buildType + "\" builds, known build types are " + KnownBuildTypes )
#			Message( 'will do ' + buildType + ' type builds' )
#		# find the build scripts
#		BaseDir = 'continuous'
#		if buildType == 'd': BaseDir = 'daily'
#		if Options.control_dir != None:
#			BaseDir = str( Options.control_dir )
#			Message( 'using "' + BaseDir + '" as control directory' )
#			BaseDir = os.sep + BaseDir # + os.sep one can never have too many separators :-)
#		ControlDir = os.path.normpath( os.getcwd() + os.sep + BaseDir )
#		if not os.path.isdir( ControlDir ):
#			raise ConfigureError( 'the control directory ' + ControlDir + ' does not exist' )
#		RunDir = ControlDir + os.sep + 'builds'
#		if not ensureEmptyWritableFolder( RunDir, True, 'Found existing run directory' ):
#			raise AutoBuildError( 'trouble preparing run directory, sorry. Exiting.' )
#		ProductBuildScripts = filter( lambda x: x.endswith( 'py' ), os.listdir( ControlDir ) )
#		ProductBuildScripts = map( lambda x: ControlDir + os.sep + x, ProductBuildScripts )
#		ProductBuildScripts = map( lambda x: os.path.normpath( x ), ProductBuildScripts )
#		ProductBuildScripts = BuildControl.DoSanityChecks( BaseDir, ProductBuildScripts, buildType )
#		# do the stuff
#		if Options.test_run:
#			Message( 'will do a test build for every product' )
#			runTestBuildJobs( Options, ProductBuildScripts )
#		elif buildType == 'c':
#			doContinuousBuilds( Options, RunDir, ProductBuildScripts )
#		elif buildType == 'd':
#			doDailyBuilds( Options, RunDir, ProductBuildScripts )
#		else:
#			raise AutoBuildError( 'build control process only knows about C and D builds' )
#		DebugN( 1, 'done, exiting.' )
#		pass

	def parseParameters ( self ):
		"""Parse command line options, give help"""
		parser = optparse.OptionParser()
		parser.add_option( "-c", "--control-dir", type = "string", dest = "control_dir",
			help = "select control folder that contains the build scripts" )
		parser.add_option( '-v', '--verbose', action = 'count', dest = 'verbosity',
			help = 'level of debug output' )
		parser.add_option( "-t", "--test-run", action = "store_true", dest = "test_run",
			help = "compile the last revision of every product for testing" )
		parser.add_option( "-b", "--build-type", type = "string", dest = "build_type",
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
		self.setBuildScripts( args )
		if not options.slaveMode:
			print( """\
+-+-+-+-+-+-+-+-+-+-+-+-+                     +-+ +-+-+-+-+ +-+-+-+-+
|m|a|k|e|-|o|-|m|a|t|i|c|                     |C| |K|D|A|B| |2|0|1|0|
+-+-+-+-+-+-+-+-+-+-+-+-+                     +-+ +-+-+-+-+ +-+-+-+-+
+-+ +-+-+-+-+-+ +-+ +-+-+-+-+-+ +-+-+-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
|i| |m|4|k|e|s| |u| |n|o|o|b|s| |k|n|o|w| |w|4|z|z| |f|0|0|b|4|r|3|d|
+-+ +-+-+-+-+-+ +-+ +-+-+-+-+-+ +-+-+-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
""" )

# "main":
# startup: get the current list of revisions, remember the highest one
# (current), and start compile jobs for every revision that comes in after
# that
# FIXME we should not exit in case a build script cannot be started, only remove this from the project list
# (easier self-repair)
try:
	ci = SimpleCI()
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

