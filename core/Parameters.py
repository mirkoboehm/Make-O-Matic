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

from core.MObject import MObject
import optparse
import sys
from core.Settings import Settings
from core.helpers.TypeCheckers import check_for_nonempty_string
from core.Exceptions import ConfigurationError
from core.helpers.GlobalMApp import mApp
from core.helpers.StringUtils import IndentedHelpFormatterWithNL

class Parameters( MObject ):
	'''Parameters parses and stores the command line parameters (arguments) of a script.'''

	def __init__( self, name = None ):
		MObject.__init__( self, name )

		self.__parser = self._getOptionParser()
		( self.__options, self.__args ) = self.__parser.parse_args() # populate options and args 

	def _getOptions( self ):
		return self.__options

	def getArgs( self ):
		return self.__args

	def _getOptionParser( self ):
		usage = "usage: %prog [options] [build|describe|query <setting>|print]"
		version = 'Make-O-Matic {0}'.format( mApp().getMomVersion() )
		description = '''\
This is a Make-O-Matic build script.

Build scripts can be executed in the following run modes:
* build:    Execute a build (default)
* query:    Query a Make-O-Matic setting by name
            (e.g. "query script.buildname")
* print:    Print information about the project's main repository.
* describe: Get an human readable description of the build process.
'''
		epilog = '''\
https://github.com/KDAB/Make-O-Matic
http://docs.kdab.com/make-o-matic/{0}/html

'''.format( mApp().getMomVersion() )

		parser = optparse.OptionParser( usage = usage, version = version, description = description, epilog = epilog, formatter = IndentedHelpFormatterWithNL() )
		parser.add_option( '-r', '--revision', action = 'store', dest = 'revision',
			help = 'repository revision to be built' )
		parser.add_option( '--tag', action = 'store', dest = 'tag',
			help = 'repository tag to be built' )
		parser.add_option( '-b', '--branch', action = 'store', dest = 'branch',
			help = 'repository branch to be built' )
		parser.add_option( '-u', '--scm-url', action = 'store', dest = 'url',
			help = 'Full SCM URL' )
		parser.add_option( '-t', '--type', action = 'store', dest = 'buildType',
			help = 'selects the build type (for example "M" (manual), "C" (continuous), "D" (daily), "S" (snapshot), "F" (full))' )
		parser.add_option( '-m', '--ignore-commit-message', action = 'store_true', dest = 'ignoreCommitMessage',
			help = 'ignore commit message commands (like "MOM:BuildType=S")' )
		parser.add_option( '--ignore-configuration-files', action = 'store_true', dest = "ignoreConfigurationFiles",
			help = "Ignore settings provided by configuration files" )
		parser.add_option( '-s', '--build-steps', action = 'store', dest = 'buildSteps',
			help = """enable or disable individual builds steps on top of the defaults for the build type, \
e.g.: -s disable-cleanup,enable-create-packages""" )
		parser.add_option( '-v', '--verbosity', action = 'count', dest = 'verbosity', default = 0,
			help = 'set the level of debug output (-v, -vv, -vvv...)' )
		return parser

	def parse( self ):
		""" read program execution options, setting up variables and proceed the dependent steps 
		The options --configure-options, -b, -l, -z have been removed.
		-b and -l are now a run mode (query).
		-z is also a run mode (print).
		-i is now an argument to the build run mode."""

		# parse options:
		( self.__options, self.__args ) = self.__parser.parse_args( sys.argv )
		# except BadOptionError, OptionValueError as e:

	def getRevision( self ):
		return self._getOptions().revision

	def getTag( self ):
		return self._getOptions().tag

	def getBranch( self ):
		return self._getOptions().branch

	def getScmLocation( self ):
		return self._getOptions().url

	def getBuildType( self ):
		buildType = self._getOptions().buildType
		if buildType:
			check_for_nonempty_string( buildType, 'The build type must be a single character!' )
			if len( buildType ) != 1:
				raise ConfigurationError( 'The build type must be a single character, not "{0}"'.format( buildType ) )
			buildType = buildType.lower()
		return buildType

	def getBuildSteps( self ):
		return self._getOptions().buildSteps

	def getIgnoreCommitMessage( self ):
		return self._getOptions().ignoreCommitMessage

	def getDebugLevel( self ):
		return self._getOptions().verbosity

	def getIgnoreConfigurationFiles( self ):
		return self._getOptions().ignoreConfigurationFiles

	def apply( self, settings ):
		assert isinstance( settings, Settings )
		if self.getRevision():
			settings.set( Settings.ProjectRevision, self.getRevision() )
		else:
			settings.set( Settings.ProjectRevision, 'latest (HEAD)' )
		if self.getTag():
			settings.set( Settings.ProjectTag, self.getTag() )
		if self.getBranch():
			settings.set( Settings.ProjectBranch, self.getBranch() )
		if self.getScmLocation():
			settings.set( Settings.ProjectSourceLocation, self.getScmLocation() )
		if self.getBuildType():
			settings.set( Settings.ProjectBuildType, self.getBuildType() )
		if self.getBuildSteps():
			settings.set( Settings.ProjectBuildSequenceSwitches, self.getBuildSteps() )
		if self.getIgnoreCommitMessage():
			settings.set( Settings.ScriptIgnoreCommitMessageCommands, self.getIgnoreCommitMessage() )
		if self.getDebugLevel():
			settings.set( Settings.ScriptLogLevel, self.getDebugLevel() )
		if len( self.getArgs() ) > 1:
			runMode = self.getArgs()[1]
			settings.set( settings.ScriptRunMode, runMode )

	def __getBuildSequenceDescription( self, buildSteps ):
		# debug info:
		texts = []
		for stepName in buildSteps:
			texts.append( '{0} ({1})'.format( stepName.getName(), 'enabled' if stepName.isEnabled() else 'disabled' ) )
		return ', '.join( texts )

	def applyBuildSequenceSwitches( self, buildSteps ):
		mApp().debugN( self, 3, 'build sequence before command line parameters: {0}'
			.format( self.__getBuildSequenceDescription( buildSteps ) ) )
		switches = self.getBuildSteps()
		if switches:
			customSteps = switches.split( ',' )
			for switch in customSteps:
				stepName = None
				enable = None
				if switch.startswith( 'enable-' ):
					stepName = switch[ len( 'enable-' ) : ].strip()
					enable = True
				elif switch.startswith( 'disable-' ):
					stepName = switch[ len( 'disable-' ) : ].strip()
					enable = False
				else:
					raise ConfigurationError( 'Build sequence switch "{0}" does not start with enable- or disable-!'
											.format( switch ) )
				# apply:
				found = False
				for step in buildSteps:
					if step.getName() == stepName:
						step.setEnabled( enable )
						found = True
						break
				if not found:
					raise ConfigurationError( 'Undefined build step "{0}" in command line arguments!'.format( stepName ) )
			mApp().debug( self, 'build sequence: {0}'.format( self.__getBuildSequenceDescription( buildSteps ) ) )
