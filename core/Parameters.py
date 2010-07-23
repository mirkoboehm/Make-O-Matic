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
import sys
from core.Settings import Settings
from core.helpers.TypeCheckers import check_for_nonempty_string

class Parameters( MObject ):
	'''Parameters parses and stores the command line parameters (arguments) of a script.'''

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.__options = None
		self.__args = None

	def _getOptions( self ):
		return self.__options

	def _getArgs( self ):
		return self.__args

	def parse( self ):
		""" read program execution options, setting up variables and proceed the dependent steps 
		The options --configure-options, -b, -l, -z have been removed.
		-b and -l are now a run mode (query).
		-z is also a run mode (print).
		-i is now an argument to the build run mode."""
		# set up the parser:
		parser = optparse.OptionParser()
		parser.add_option( '-r', '--revision', action = 'store', dest = 'revision',
			help = 'repository revision to be built' )
		parser.add_option( '-u', '--scm-url', action = 'store', dest = 'url',
			help = 'Full SCM URL' )
		parser.add_option( '-e', '--email-recipients', action = 'store', dest = 'mailTo',
			help = 'comma separated list of email recipients for emailed build reports' )
		parser.add_option( '-t', '--type', action = 'store', dest = 'buildType',
			help = 'selects the build type (for example manual, continuous, daily, snapshot, full)' )
		parser.add_option( '-m', '--ignore-commit-message', action = 'store_true', dest = 'ignoreCommitMessage',
			help = 'ignore commit message commands (like "MOM:BuildType=S")' )
		parser.add_option( '-s', '--build-steps', action = 'store', dest = 'buildSteps',
			help = 'enable or disable individual builds steps on top of the defaults for the build type' )
		parser.add_option( '-v', '--verbose', action = 'count', dest = 'verbosity', default = 0,
			help = 'level of debug output' )
		# parse options:
		( self.__options, self.__args ) = parser.parse_args( sys.argv )
		# except BadOptionError, OptionValueError as e:

	def getRevision( self ):
		return self._getOptions().revision

	def getScmLocation( self ):
		return self._getOptions().url

	def getBuildType( self ):
		buildType = self._getOptions().buildType
		if buildType:
			check_for_nonempty_string( buildType, 'The build type must be a single character!' )
			buildType = buildType.lower()
# FIXME Mirko
#		if buildType not in self.knownBuildTypes():
#				raise MomError( 'There are only these build types: ' + self.knownBuildTypes() )
#		if self.getBuildType() == 'e' and ( options.buildSteps == None or 'enable' not in options.buildSteps ):
#				raise AutoBuildError( '(E)mpty build type requires to set the -s option, and to enable at least one build step (-s)' )
		return buildType

	def getBuildSteps( self ):
		return self._getOptions().buildSteps

	def getRecipients( self ):
		return self._getOptions().mailTo

	def getIgnoreCommitMessage( self ):
		return self._getOptions().ignoreCommitMessage

	def getDebugLevel( self ):
		return self._getOptions().verbosity

	def apply( self, settings ):
		assert isinstance( settings, Settings )
		if self.getRevision():
			settings.set( Settings.ProjectRevision, self.getRevision() )
		if self.getScmLocation():
			settings.set( Settings.ProjectSourceLocation, self.getScmLocation() )
		if self.getBuildType():
			settings.set( Settings.ProjectBuildType, self.getBuildType() )
		if self.getBuildSteps():
			settings.set( Settings.ProjectBuildSequenceSwitches, self.getBuildSteps() )
		if self.getRecipients():
			settings.set( Settings.EmailReporterRecipients, self.getRecipients() )
		if self.getIgnoreCommitMessage():
			settings.set( Settings.ScriptIgnoreCommitMessageCommands, self.getIgnoreCommitMessage() )
		if self.getDebugLevel():
			settings.set( Settings.ScriptLogLevel, self.getDebugLevel() )
		if len( self._getArgs() ) > 1:
			runMode = self._getArgs()[1]
			settings.set( settings.ScriptRunMode, runMode )