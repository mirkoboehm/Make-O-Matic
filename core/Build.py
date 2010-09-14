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
from core.MApplication import MApplication
from core.Project import Project
from core.Exceptions import ConfigurationError, MomError
from core.Settings import Settings
from core.Parameters import Parameters
from core.helpers.MachineInfo import machine_info

class Build( MApplication ):
	'''Build represents the facilities provided by the currently running build script.
	It contains the loggers and reporters, for example. It also maintains the settings.'''

	def __init__( self, minimumMomVersion = None, name = None, parent = None ):
		MApplication.__init__( self, minimumMomVersion, name, parent )
		self.__project = None
		self.__parameters = Parameters()

	def getParameters( self ):
		return self.__parameters

	def _initialize( self ):
		'''Determine the script run settings. 
		In the constructor, defaults will be applied. 
		First, configuration files will be parsed.
		Second, command line arguments will be applied. 
		Third, commit message commands will be applied. This can be disabled by a parameter (step three).
		On error, a subclass of MomException is thrown.
		Logging and reporting is not available at this stage yet.'''
		# first, parse configuration files:
		self.getSettings().evalConfigurationFiles()
		# second, apply parameters:
		self.getParameters().apply( self.getSettings() )
		# third, apply commit message commands:
		# FIXME

	def setProject( self, project ):
		'''Every build has one master project. This method sets the master project.'''
		self.addProject( project )
		self.__project = project

	def getProject( self ):
		'''Return the master project for this build.'''
		return self.__project

	def addProject( self, project ):
		if not isinstance( project, Project ):
			raise ConfigurationError( 'The project variable needs to be an instance of the Project class!' )
		self.addChild( project )

	def printAndExit( self ):
		# program name, "print", argument, [options] 
		if len( self.getParameters()._getArgs() ) < 3:
			raise MomError( 'Please specify parameter to print!' )
		command = self.getParameters()._getArgs()[2]
		options = self.getParameters()._getArgs()[3:]
		commands = {
			'revisions-since' : [ self.getProject().getScm().printRevisionsSince, 'print revisions committed since specified revision' ],
			'current-revision': [ self.getProject().getScm().printCurrentRevision, 'print current revision' ]
		}
		if command in commands:
			method = commands[ command ][0]
			print( method( options ) )
		else:
			text = 'Unknown command "{0}" for run mode "print". Known commands are:'.format( command )
			for cmd in commands:
				text += '\n   {0}: {1}'.format( cmd, commands[ cmd ][1] )
			raise ConfigurationError( text )

	def run( self ):
		if self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Describe:
			self.describeRecursively()
		elif self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Build:
			MApplication.run( self )
		else:
			raise MomError( 'run can only be called in describe and build run modes' )

	def _buildAndReturn( self ):
		'''Overloaded method that implements the run modes.'''
		if self.getSettings().get( Settings.ScriptRunMode ) in ( Settings.RunMode_Build, Settings.RunMode_Describe ):
			MApplication._buildAndReturn( self ) # use base class implementation
		elif self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Query:
			self.runPreFlightChecks()
			# filter script name, 'query'
			self.querySettings( self.getParameters()._getArgs()[2:] )
		elif self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Print:
			self.runPreFlightChecks()
			self.printAndExit()
		else:
			assert self.getSettings().get( Settings.ScriptRunMode ) not in Settings.RunModes
			raise MomError( 'Unknown run mode "{0}". Known run modes are: {1}'.format( 
					self.getSettings().get( Settings.ScriptRunMode ),
					', '.join( Settings.RunModes ) ) )

	def createXmlNode( self, document ):
		node = MApplication.createXmlNode( self, document )

		for key, value  in machine_info().items():
			node.attributes[key] = value

		return node
