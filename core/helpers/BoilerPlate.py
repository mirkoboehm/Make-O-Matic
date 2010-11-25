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

from core.Build import Build
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
from core.loggers.ConsoleLogger import ConsoleLogger
from core.Exceptions import MomException
import sys
from core.Project import Project
from core.plugins.reporters.ConsoleReporter import ConsoleReporter
from core.plugins.reporters.XmlReportGenerator import XmlReportGenerator
from core.Configuration import Configuration

def getBuild( buildName = "MOMBuild", minimumMomVersion = "0.5.0" ):
	try:
		build = Build( minimumMomVersion, buildName )
		build.getParameters().parse()
		mApp().getSettings().set( Settings.ScriptLogLevel, build.getParameters().getDebugLevel() )
		logger = ConsoleLogger()
		build.addLogger( logger )
		build.addPlugin( XmlReportGenerator() )
		build.addPlugin( ConsoleReporter() )

		build.initialize()
		return build
	except MomException as e:
		print( 'Error during setup, return code {0}: {1}'.format( e.getReturnCode() , str( e ) ), sys.stderr )
		sys.exit( e.getReturnCode() )

def getProject( build, projectName = "MOMProject",
				projectVersionNumber = "0.0.1", projectVersionName = None,
				scmUrl = None, scmRevision = None, scmBranch = None, scmTag = None ):
	'''Create a standard default Project object.
	A default project will have a ConsoleLogger, and a ConsoleReporter.
	makeProject will also parse the configuration files.
	'''
	project = Project( projectName )
	# the command line parameter takes precedence
	url = build.getParameters().getScmLocation() or scmUrl
	revision = build.getParameters().getRevision() or scmRevision
	branch = build.getParameters().getBranch() or scmBranch
	tag = build.getParameters().getTag() or scmTag
	mApp().getSettings().set( Settings.ProjectVersionNumber, projectVersionNumber )
	mApp().getSettings().set( Settings.ProjectVersionName, projectVersionName )
	mApp().getSettings().set( Settings.ProjectSourceLocation, url )
	mApp().getSettings().set( Settings.ProjectRevision, revision )
	mApp().getSettings().set( Settings.ProjectBranch, branch )
	mApp().getSettings().set( Settings.ProjectTag, tag )
	project.createScm( url )
	build.setProject( project )
	return project

def getBuildProject( buildName = None, minimumMomVersion = None,
		projectName = None,
		projectVersionNumber = None, projectVersionName = None,
		scmUrl = None ):
	# If the only one of the project/build names is set, initialise both with the same value
	if buildName and not projectName:
		projectName = buildName
	if projectName and not buildName:
		buildName = projectName
	build = getBuild( buildName, minimumMomVersion )
	project = getProject( build, projectName, projectVersionNumber, projectVersionName, scmUrl )
	return build, project

def getBuildConfiguration( buildName = None, minimumMomVersion = None,
		projectName = None,
		projectVersionNumber = None, projectVersionName = None,
		scmUrl = None ):
	build, project = getBuildProject( buildName, minimumMomVersion, projectName,
												projectVersionNumber, projectVersionName, scmUrl )
	configuration = Configuration( project.getName(), project )
	return build, configuration
