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
from socket import gethostname
import os

class Defaults( MObject ):
	"""Defaults stores all hard-coded default values of make-o-matic."""

	# Constants (build script values)
	RunMode_Build = 'build'
	RunMode_Query = 'query'
	RunMode_Print = 'print'
	RunMode_Describe = 'describe'
	RunModes = [ RunMode_Build, RunMode_Query, RunMode_Print, RunMode_Describe ]
	EnvironmentExpansionMode_Ignore = 1
	EnvironmentExpansionMode_BuildHighestScoring = 2
	EnvironmentExpansionMode_BuildAll = 3
	EnvironmentsExpansionModes = {
		EnvironmentExpansionMode_Ignore : 'EnvironmentExpansionMode_Ignore: do not expand environments',
		EnvironmentExpansionMode_BuildHighestScoring : 'EnvironmentExpansionMode_BuildHighestScoring: expand environments, '
			+ 'build against the best scoring one',
		EnvironmentExpansionMode_BuildAll : 'EnvironmentExpansionMode_BuildAll: expand environments, '
			+ 'build against all matches'
	}
	# Constants (setting variable names)
	# ----- script settings:
	ScriptLogLevel = 'script.loglevel'
	ScriptClientName = 'script.clientname'
	ScriptIgnoreCommitMessageCommands = 'script.ignorecommitmessagecommands'
	ScriptRunMode = 'script.runmode'
	ScriptBuildName = 'script.buildname'
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
	ProjectBuildSequence = 'project.buildsequence'
	ProjectSourceLocation = 'project.sourcelocation'
	ProjectRevision = 'project.revision'
	ProjectTag = 'project.tag'
	ProjectBranch = 'project.branch'
	ProjectSourceDir = 'project.srcdir'
	ProjectPackagesDir = 'project.packagesdir'
	ProjectDocsDir = 'project.docsdir'
	ProjectTempDir = 'project.tempdir'
	ProjectLogDir = 'project.logdir'
	ProjectBuildSequenceSwitches = 'project.buildsequenceswitches'
	# ----- Configuration settings (not specific to individual configurations, but to all)
	ConfigurationBuildDir = 'configuration.builddir'
	ConfigurationTargetDir = 'configuration.targetdir'
	# ----- auto-detected environment settings:
	EnvironmentsBaseDir = 'environments.basedir'
	EnvironmentsApplicableBuildTypes = 'environments.applicablebuildtypes'
	EnvironmentsExpansionModeMapping = 'environments.expansionmodes'
	# ----- System path settings:
	SystemExtraPaths = 'system.extrapaths'
	# ----- Build settings:
	BuildMoveOldDirectories = 'build.moveolddirectories'
	# ----- Builder settings
	MakeBuilderInstallTarget = 'configuration.builder.make.installtarget'
	# ----- CMake Builder settings
	CMakeBuilderTool = 'configuration.builder.cmake.toolname'
	# ----- RSync publisher settings (should be set in .mom/config.py):
	RSyncPublisherUploadLocation = 'publisher.rsync.uploadlocation'
	# ----- EmailReporter settings:
	EmailReporterSender = 'emailreporter.sender'
	EmailReporterDefaultRecipients = 'emailreporter.defaultrecipients'
	EmailReporterConfigurationErrorRecipients = 'emailreporter.configurationerrorrecipients'
	EmailReporterMomErrorRecipients = 'emailreporter.momerrorrecipients'
	EmailReporterNotifyCommitterOnFailure = 'emailreporter.notifycommitteronfailure'
	# ----- Emailer settings:
	EmailerSmtpServer = 'emailer.smtpserver'
	EmailerServerPort = 'emailer.serverport'
	EmailerTimeout = 'emailer.timeout'
	EmailerUseTls = 'emailer.usetls'
	EmailerDoLogin = 'emailer.dologin'
	EmailerUsername = 'emailer.username'
	EmailerPassword = 'emailer.password'
	# ----- simple_ci settings: 
	SimpleCIBuildJobCap = 'simple_ci.build.cap'

	def getDefaultSettings( self ):
		home = os.path.expanduser( "~" )

		defaultSettings = {}
		# ----- store the make-o-matic version these scripts use:
		defaultSettings[ Defaults.MomVersionNumber ] = '0.5.0'
		# ----- script settings:
		defaultSettings[ Defaults.ScriptLogLevel ] = 0
		defaultSettings[ Defaults.ScriptClientName ] = gethostname()
		defaultSettings[ Defaults.ScriptRunMode ] = Defaults.RunMode_Build
		defaultSettings[ Defaults.ScriptIgnoreCommitMessageCommands ] = False
		# ----- internal settings
		defaultSettings[ Defaults.MomDebugIndentVariable ] = 'MOM_INTERNAL_DEBUG_INDENT'
		# ----- project settings:
		defaultSettings[ Defaults.ProjectExecutomatLogfileName ] = 'execution.log'
		defaultSettings[ Defaults.ProjectBuildType ] = 'm'
		defaultSettings[ Defaults.ProjectBuildSequence] = [ # name, modes, execute-on-failure
			[ 'build-create-folders', 'mcdhpsf', False ],
			[ 'project-checkout', 'mcdhpsf', False ],
			[ 'conf-export-sources', 'mcdhpsf', False ],
			[ 'conf-configure', 'mcdhpsf', False ],
			[ 'conf-make', 'mcdhpsf', False ],
			[ 'conf-make-test', 'mcdhpsf', False ],
			[ 'conf-make-install', 'mcdhpsf', False ],
			[ 'conf-package', 'dsfp', False ],
			[ 'project-create-docs', 'mcdhpsf', False ],
			[ 'project-package', 'dsf', False ],
			[ 'project-upload-docs', 'dsf', False ],
			[ 'project-upload-packages', 'dsf', False ],
			[ 'project-cleanup-docs', 'cdsf', True ],
			[ 'project-cleanup-packages', 'cdsf', True ],
			[ 'build-cleanup', 'mcdsf', True ] ]
		defaultSettings[ Defaults.ProjectBuildTypeDescriptions ] = { # build type to descriptive text
			'e' : 'Empty build. All build steps are disabled. Useful for debugging build scripts.',
			'm' : 'Manual build. Does not modify environment variables. Deletes temporary folders.',
			'c' : 'Continuous build. Builds configurations against the best scoring matching environment. Deletes temporary folders.',
			'd' : 'Daily build. Builds configurations against every matching environment. Deletes temporary folders.',
			'h' : 'Hacker build. Similar to manual builds. Does not delete temporary folders.',
			'p' : '1337 coder build. Similar to daily builds. Does not delete temporary folders.',
			's' : 'Snapshot build. Similar to daily builds. Creates and uploads packages and documentation.',
			'f' : 'Full build. All build steps are enabled. Useful for debugging build scripts.'
		}
		defaultSettings[ Defaults.ProjectSourceDir ] = 'src'
		defaultSettings[ Defaults.ProjectPackagesDir ] = 'packages'
		defaultSettings[ Defaults.ProjectDocsDir ] = 'docs'
		defaultSettings[ Defaults.ProjectTempDir ] = 'tmp'
		defaultSettings[ Defaults.ProjectLogDir ] = 'log'
		# ----- configuration settings:
		defaultSettings[ Defaults.ConfigurationBuildDir ] = 'build'
		defaultSettings[ Defaults.ConfigurationTargetDir ] = 'install'
		defaultSettings[ Defaults.MakeBuilderInstallTarget ] = 'install'
		defaultSettings[ Defaults.EnvironmentsBaseDir ] = os.path.join( home, 'MomEnvironments' )
		defaultSettings[ Defaults.EnvironmentsExpansionModeMapping ] = {
			'c' : Defaults.EnvironmentExpansionMode_BuildHighestScoring,
			'd' : Defaults.EnvironmentExpansionMode_BuildAll,
			's' : Defaults.EnvironmentExpansionMode_BuildAll,
			'p' : Defaults.EnvironmentExpansionMode_BuildAll,
			'f' : Defaults.EnvironmentExpansionMode_BuildAll
		}
		defaultSettings[ Defaults.EnvironmentsApplicableBuildTypes ] = 'cdpsf'
		# ----- System path settings:
		defaultSettings[ Defaults.SystemExtraPaths ] = []
		# ----- Build settings:
		defaultSettings[ Defaults.BuildMoveOldDirectories ] = True
		# ----- EmailReporter settings:
		defaultSettings[ Defaults.EmailReporterMomErrorRecipients] = None
		defaultSettings[ Defaults.EmailReporterNotifyCommitterOnFailure ] = True
		# ----- simple_ci settings:
		defaultSettings[ Defaults.SimpleCIBuildJobCap ] = 8

		return defaultSettings
