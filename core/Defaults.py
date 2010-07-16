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
from socket import gethostname
from core.helpers.TypeCheckers import check_for_nonempty_string
from core.Exceptions import ConfigurationError

class Defaults( MObject ):
	"""Defaults stores all hard-coded default values of make-o-matic."""

	# Constants (build script values)
	RunMode_Build = 'build'
	RunMode_Query = 'query'
	RunMode_Print = 'print'
	RunModes = [ RunMode_Build, RunMode_Query, RunMode_Print ]

	# Constants (setting variable names)
	# ----- script settings:
	ScriptLogLevel = 'script.loglevel'
	ScriptClientName = 'script.clientname'
	ScriptIgnoreCommitMessageCommands = 'script.ignorecommitmessagecommands'
	ScriptRunMode = 'script.runmode'
	# ----- project settings 
	ProjectName = 'project.name'
	ProjectExecutomatLogfileName = 'project.executomat.logfilename'
	ProjectBuildType = 'project.buildtype'
	ProjectBuildSteps = 'project.buildsteps'
	ProjectSourceLocation = 'project.sourcelocation'
	ProjectRevision = 'project.revision'
	ProjectBuildSequenceSwitches = 'project.buildsequenceswitches'
	# ----- reporter settings:
	EmailReporterSender = 'reporter.email.sender'
	EmailReporterRecipients = 'reporter.email.recipient'

	def __init__( self ):
		'''Constructor'''
		MObject.__init__( self )
		self.__settings = {}
		# store defaults:
		# ----- script settings:
		self.getSettings()[ Defaults.ScriptLogLevel ] = 0
		self.getSettings()[ Defaults.ScriptClientName ] = gethostname()
		self.getSettings()[ Defaults.ScriptRunMode ] = Defaults.RunMode_Build
		self.getSettings()[ Defaults.ScriptIgnoreCommitMessageCommands ] = False
		# ----- project settings:
		self.getSettings()[ Defaults.ProjectExecutomatLogfileName ] = 'execution.log'
		self.getSettings()[ Defaults.ProjectBuildType ] = 'm'
		self.getSettings()[ Defaults.ProjectBuildSteps] = [ # name, modes
			[ 'project-create-folders', 'mcdsf' ],
			[ 'project-checkout', 'mcdsf' ],
			[ 'project-build-configurations', 'mcdsf' ],
			[ 'project-create-docs', 'mcdsf' ],
			[ 'project-package', 'dsf' ],
			[ 'project-upload-docs', 'dsf' ],
			[ 'project-upload-packages', 'dsf' ],
			[ 'project-cleanup-docs', 'cdsf' ],
			[ 'project-cleanup-packages', 'cdsf' ],
			[ 'project-cleanup', 'mcdsf' ] ]

	def getSettings( self ):
		return self.__settings

	# FIXME type checking
	def get( self, name, required = True ):
		check_for_nonempty_string( name, 'The setting name must be a nonempty string!' )
		try:
			return self.getSettings()[ name ]
		except KeyError:
			if required:
				raise ConfigurationError( 'The required setting "{0}" is undefined!'.format( name ) )
			else:
				return None

	def set( self, name, value ):
		check_for_nonempty_string( name, 'The setting name must be a nonempty string!' )
		self.getSettings()[ name ] = value

