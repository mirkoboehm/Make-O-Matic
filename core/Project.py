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

from __future__ import print_function

import sys
from core.modules.FolderManager import FolderManager
from core.modules.SourceCodeProvider import SourceCodeProvider
from core.helpers.TimeKeeper import TimeKeeper
from core.Settings import Settings
from core.Exceptions import MomError
from core.modules.scm.Factory import SourceCodeProviderFactory
from core.helpers.PathResolver import PathResolver
from core.modules.reporters.ConsoleReporter import ConsoleReporter
from core.Instructions import Instructions
from core.MApplication import mApp

"""A Project represents an entity to build. 
FIXME documentation
"""
class Project( Instructions ):

	def __init__( self, projectName ):
		"""Set up the build steps, parse the command line arguments."""
		Instructions.__init__( self, projectName )
		mApp().getSettings().set( Settings.ProjectName, projectName )
		self.__timeKeeper = TimeKeeper()
		self.__scm = None
		self.__folderManager = FolderManager( self )
		self.addPlugin( self.getFolderManager() )

	def createScm( self, description ):
		factory = SourceCodeProviderFactory()
		scm = factory.makeScmImplementation( description )
		scm.setSrcDir( PathResolver( self.getFolderManager().getSourceDir ) )
		self.setScm( scm )

	def setScm( self, scm ):
		if self.getScm():
			raise MomError( 'The master SCM can only be set once!' )
		if not isinstance( scm, SourceCodeProvider ):
			raise MomError( 'SCMs need to re-implement the SourceCodeProvider class!' )
		self.__scm = scm
		self.addPlugin( scm )

	def getScm( self ):
		return self.__scm

	def getFolderManager( self ):
		return self.__folderManager

	def getTimeKeeper( self ):
		return self.__timeKeeper

	def setup( self ):
		assert False # this is the wrong setup method!
		for step in mApp().getSettings().calculateBuildSequence( self ):
			self.getExecutomat().addStep( step )

	def printAndExit( self ):
		# program name, "print", argument, [options] 
		if len( self.getParameters()._getArgs() ) < 3:
			raise MomError( 'Please specify parameter to print!' )
		command = self.getParameters()._getArgs()[2]
		options = self.getParameters()._getArgs()[3:]
		commands = {
			'revisions-since' : [ self.getScm().printRevisionsSince, 'print revisions committed since specified revision' ],
			'current-revision': [ self.getScm().printCurrentRevision, 'print current revision' ]
		}
		if command in commands:
			method = commands[ command ][0]
			print( method( self, options ) )
			sys.exit( 0 )
		else:
			text = 'Unknown command "{0}" for run mode "print". Known commands are:'.format( command )
			for cmd in commands:
				text += '\n   {0}: {1}'.format( cmd, commands[ cmd ][1] )
			print( text, file = sys.stderr )
			sys.exit( 1 )

def makeProject( projectName = None,
				projectVersionNumber = None, projectVersionName = None,
				scmUrl = None ):
	'''Create a standard default Project object.
	A default project will have a ConsoleLogger, and a ConsoleReporter.
	makeProject will also parse the configuration files.
	'''
	project = Project( projectName )
	reporter = ConsoleReporter()
	project.addPlugin( reporter )
	mApp().getSettings().set( Settings.ProjectVersionNumber, projectVersionNumber )
	mApp().getSettings().set( Settings.ProjectVersionName, projectVersionName )
	project.createScm( scmUrl )
	return project
