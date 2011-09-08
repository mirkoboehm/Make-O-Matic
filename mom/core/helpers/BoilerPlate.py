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

from mom.core.loggers import FileLogger
from mom.core.Build import Build
from mom.core.Configuration import Configuration
from mom.core.Exceptions import MomException
from mom.core.Project import Project
from mom.core.Settings import Settings
from mom.core.helpers.GlobalMApp import mApp
from mom.core.loggers.ConsoleLogger import ConsoleLogger
from mom.plugins.helpers.XmlReportGenerator import XmlReportGenerator
from mom.plugins.reporters.ConsoleReporter import ConsoleReporter
from mom.plugins.selftest.IntegrityChecker import IntegrityChecker
import sys

def getBuild( name, minimumMomVersion ):
	try:
		build = Build( minimumMomVersion, name )
		build.getParameters().parse()
		mApp().getSettings().set( Settings.ScriptLogLevel, build.getParameters().getDebugLevel() )
		build.addLogger( ConsoleLogger() )
		build.addLogger( FileLogger() )
		build.addPlugin( XmlReportGenerator() )
		build.addPlugin( ConsoleReporter() )
		build.addPlugin( IntegrityChecker() )

		build.initialize()
		return build
	except MomException as e:
		print( 'Error during setup, return code {0}: {1}'.format( e.getReturnCode() , str( e ) ), sys.stderr )
		sys.exit( e.getReturnCode() )

def getProject( build, name, url, version, revision, branch, tag, versionName ):
	'''Create a standard default getProject object.
	A default project will have a ConsoleLogger, and a ConsoleReporter.
	makeProject will also parse the configuration files.
	'''
	project = Project( name )
	# the command line parameter takes precedence
	url = build.getParameters().getScmLocation() or url
	revision = build.getParameters().getRevision() or revision
	if build.getParameters().getBranch() or build.getParameters().getTag():
		# if either branch or tag are specified on the command line, reset both and only use the command line selection:
		branch = None
		tag = None
	branch = build.getParameters().getBranch() or branch
	tag = build.getParameters().getTag() or tag
	mApp().getSettings().set( Settings.ProjectVersionNumber, version )
	mApp().getSettings().set( Settings.ProjectVersionName, versionName )
	mApp().getSettings().set( Settings.ProjectSourceLocation, url )
	mApp().getSettings().set( Settings.ProjectRevision, revision )
	mApp().getSettings().set( Settings.ProjectBranch, branch )
	mApp().getSettings().set( Settings.ProjectTag, tag )
	project.createScm( url, branch, tag, revision )
	build.setProject( project )
	return project

def BuildProject( name, url, version = "0.0.1", revision = None, branch = None, tag = None,
				versionName = None, build = None, minimumMomVersion = "0.5.0" ):
	if name and not build:
		build = name
	build = getBuild( build, minimumMomVersion )
	project = getProject( build, name, url, version, revision, branch, tag, versionName )
	return build, project

def BuildConfiguration( name, url, version = "0.0.1", revision = None, branch = None, tag = None,
					versionName = None, build = None, minimumMomVersion = "0.5.0" ):
	build, project = BuildProject( name, url, version, revision, branch, tag, versionName, build, minimumMomVersion )
	configuration = Configuration( project.getName(), project )
	return build, configuration
