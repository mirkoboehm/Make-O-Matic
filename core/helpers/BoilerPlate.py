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
from core.Build import Build
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
from core.loggers.ConsoleLogger import ConsoleLogger
from core.Exceptions import MomException
import sys
from core.Project import Project
from core.modules.reporters.ConsoleReporter import ConsoleReporter

def setupStandardBuild( buildName = None, minimumMomVersion = None ):
	try:
		build = Build( buildName, minimumMomVersion )
		build.getParameters().parse()
		mApp().getSettings().set( Settings.ScriptLogLevel, build.getParameters().getDebugLevel() )
		logger = ConsoleLogger()
		build.addLogger( logger )
		build._initialize()
		return build
	except MomException as e:
		print( 'Error during setup, return code {0}: {1}'.format( e.getReturnCode() , str( e ) ), file = sys.stderr )
		sys.exit( e.getReturnCode() )

def setupStandardProject( build, projectName = None,
				projectVersionNumber = None, projectVersionName = None,
				scmUrl = None ):
	'''Create a standard default Project object.
	A default project will have a ConsoleLogger, and a ConsoleReporter.
	makeProject will also parse the configuration files.
	'''
	project = Project( projectName )
	# the command line parameter takes precedence
	url = build.getParameters().getScmLocation() or scmUrl
	reporter = ConsoleReporter()
	project.addPlugin( reporter )
	mApp().getSettings().set( Settings.ProjectVersionNumber, projectVersionNumber )
	mApp().getSettings().set( Settings.ProjectVersionName, projectVersionName )
	project.createScm( url )
	build.setProject( project )
	return project

def setupStandardBuildAndProject( buildName = None, minimumMomVersion = None,
		projectName = None,
		projectVersionNumber = None, projectVersionName = None,
		scmUrl = None ):
	build = setupStandardBuild( buildName, minimumMomVersion )
	project = setupStandardProject( build, projectName, projectVersionNumber, projectVersionName, scmUrl )
	return build, project