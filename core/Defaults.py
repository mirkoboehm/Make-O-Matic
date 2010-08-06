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
	# ----- internal settings
	MomVersionNumber = 'mom.version.number'
	MomDebugIndentVariable = 'mom.debug.indentvariable'
	# ----- project settings 
	ProjectName = 'project.name'
	ProjectVersionNumber = 'project.version.number'
	ProjectVersionName = 'project.version.name'
	ProjectExecutomatLogfileName = 'project.executomat.logfilename'
	ProjectBuildType = 'project.buildtype'
	ProjectBuildTypeDescriptions = 'project.buildtypedescriptions'
	ProjectBuildSteps = 'project.buildsteps'
	ProjectSourceLocation = 'project.sourcelocation'
	ProjectRevision = 'project.revision'
	ProjectSourceDir = 'project.srcdir'
	ProjectPackagesDir = 'project.packagesdir'
	ProjectDocsDir = 'project.docsdir'
	ProjectTempDir = 'project.tempdir'
	ProjectLogDir = 'project.logdir'
	ProjectBuildSequenceSwitches = 'project.buildsequenceswitches'
	# ----- Configuration settings (not specific to individual configurations, but to all)
	ConfigurationBuildSteps = 'configuration.buildsteps'
	# ----- RSync publisher settings (should be set in .mom/config.py):
	RSyncPublisherUploadLocation = 'publisher.rsync.uploadlocation'
	# ----- reporter settings:
	EmailReporterSender = 'reporter.email.sender'
	EmailReporterRecipients = 'reporter.email.recipient'
	# ----- simple_ci settings: 
	SimpleCIBuildJobCap = 'simple_ci.build.cap'

	def __init__( self ):
		'''Constructor'''
		MObject.__init__( self )
		self.__settings = {}
		# store defaults:
		# ----- store the make-o-matic version these scripts use:
		self.getSettings()[ Defaults.MomVersionNumber ] = '0.5.0'
		# ----- script settings:
		self.getSettings()[ Defaults.ScriptLogLevel ] = 0
		self.getSettings()[ Defaults.ScriptClientName ] = gethostname()
		self.getSettings()[ Defaults.ScriptRunMode ] = Defaults.RunMode_Build
		self.getSettings()[ Defaults.ScriptIgnoreCommitMessageCommands ] = False
		# ----- internal settings
		self.getSettings()[ Defaults.MomDebugIndentVariable ] = 'MOM_INTERNAL_DEBUG_INDENT'
		# ----- project settings:
		self.getSettings()[ Defaults.ProjectExecutomatLogfileName ] = 'execution.log'
		self.getSettings()[ Defaults.ProjectBuildType ] = 'm'
		self.getSettings()[ Defaults.ProjectBuildSteps] = [ # name, modes, execute-on-failure
			[ 'project-create-folders', 'mcdhpsf', False ],
			[ 'project-checkout', 'mcdhpsf', False ],
			[ 'project-build-configurations', 'mcdhpsf', False ],
			[ 'project-create-docs', 'mcdhpsf', False ],
			[ 'project-package', 'dsf', False ],
			[ 'project-upload-docs', 'dsf', False ],
			[ 'project-upload-packages', 'dsf', False ],
			[ 'project-cleanup-docs', 'cdsf', True ],
			[ 'project-cleanup-packages', 'cdsf', True ],
			[ 'project-cleanup', 'mcdsf', True ] ]
		self.getSettings()[ Defaults.ProjectBuildTypeDescriptions ] = { # build type to descriptive text
			'e' : 'Empty build. All build steps are disabled. Useful for debugging build scripts.',
			'm' : 'Manual build. Does not modify environment variables. Deletes temporary folders.',
			'c' : 'Continuous build. Builds configurations against the latest matching environment. Deletes temporary folders.',
			'd' : 'Daily build. Builds configurations against every matching environment. Deletes temporary folders.',
			'h' : 'Hacker build. Similar to manual builds. Does not delete temporary folders.',
			'p' : '1337 coder build. Similar to daily builds. Does not delete temporary folders.',
			's' : 'Snapshot build. Similar to daily builds. Creates and uploads packages and documentation.',
			'f' : 'Full build. All build steps are enabled. Useful for debugging build scripts.'
		}
		self.getSettings()[ Defaults.ProjectSourceDir ] = 'src'
		self.getSettings()[ Defaults.ProjectPackagesDir ] = 'packages'
		self.getSettings()[ Defaults.ProjectDocsDir ] = 'docs'
		self.getSettings()[ Defaults.ProjectTempDir ] = 'tmp'
		self.getSettings()[ Defaults.ProjectLogDir ] = 'log'
		# ----- configuration settings:
		self.getSettings()[ Defaults.ConfigurationBuildSteps ] = [ # name, modes, execute-on-failure
			[ 'conf-create-folders', 'mcdhpsf', False ],
			[ 'conf-export-sources', 'mcdhpsf', False ],
			[ 'conf-configure', 'mcdhpsf', False ],
			[ 'conf-make', 'mcdhpsf', False ],
			[ 'conf-make-test', 'mcdhpsf', False ],
			[ 'conf-make-install', 'mcdhpsf', False ],
			[ 'conf-package', 'dsf', False ],
			[ 'conf-cleanup', 'mcdhpsf', False ],
		]
		# ----- simple_ci settings:
		self.getSettings()[ Defaults.SimpleCIBuildJobCap ] = 8

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

