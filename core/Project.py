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

import sys
from core.MObject import MObject
from core.modules.FolderManager import FolderManager
from core.modules.SourceCodeProvider import SourceCodeProvider
from core.loggers.ConsoleLogger import ConsoleLogger
from core.loggers.Logger import Logger
from core.helpers.TypeCheckers import check_for_nonnegative_int
from core.helpers.TimeKeeper import TimeKeeper
from core.executomat.Executomat import Executomat
from core.Settings import Settings
from core.Exceptions import InterruptedException, MomError, MomException
from core.Parameters import Parameters
from core.helpers.VersionChecker import checkMinimumMomVersion
from core.modules.scm.Factory import SourceCodeProviderFactory
from core.helpers.PathResolver import PathResolver

"""A Project represents an entity to build. 
FIXME documentation
"""
class Project( MObject ):

	def __init__( self, projectName, minimalMomVersion = None ):
		"""Set up the build steps, parse the command line arguments."""
		MObject.__init__( self, projectName )
		self.__settings = Settings()
		self.getSettings().set( Settings.ProjectName, projectName )
		self.__timeKeeper = TimeKeeper()
		self.__parameters = Parameters()
		self.__scm = None
		self.__loggers = []
		self.__plugins = []
		self.__returnCode = 0
		self.__executomat = Executomat( self, 'Exec-o-Matic' )
		try:
			self.getSettings().initialize( self )
		except MomException as e:
			print( 'Error during setup, return code {0}: {1}'.format( e.getReturnCode() , str( e ) ), file = sys.stderr )
			sys.exit( e.getReturnCode() )
		logger = ConsoleLogger( self.getSettings().get( Settings.ScriptLogLevel ) )
		self.addLogger( logger )
		self.__folderManager = FolderManager( self )
		self.addPlugin( self.getFolderManager() )
		checkMinimumMomVersion( self, minimalMomVersion )

	def getSettings( self ):
		return self.__settings

	def getParameters( self ):
		return self.__parameters

	def getMomVersion( self ):
		return '0.5.0'

	def createScm( self, description ):
		factory = SourceCodeProviderFactory()
		scm = factory.makeScmImplementation( self, description )
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

	def getPlugins( self ):
		return self.__plugins

	def addPlugin( self, plugin ):
		self.__plugins.append( plugin )

	def addLogger( self, logger ):
		if not isinstance( logger, Logger ):
			raise MomError( 'Loggers need to re-implement the Logger class!' )
		self.__loggers.append( logger )
		self.addPlugin( logger )

	def getLoggers( self ):
		return self.__loggers

	def getTimeKeeper( self ):
		return self.__timeKeeper

	def setReturnCode( self, code ):
		check_for_nonnegative_int( code, "The return code of the build script has to be a non-negative integer number!" )
		self.__returnCode = code

	def getReturnCode( self ):
		return self.__returnCode

	def getExecutomat( self ):
		return self.__executomat

	def message( self, mobject, text ):
		[ logger.message( self, mobject, text ) for logger in self.getLoggers() ]

	def debug( self, mobject, text ):
		[ logger.debug( self, mobject, text ) for logger in self.getLoggers() ]

	def debugN( self, mobject, level, text ):
		[ logger.debugN( self, mobject, level, text ) for logger in self.getLoggers() ]

	def setup( self ):
		for step in self.getSettings().calculateBuildSequence( self ):
			self.getExecutomat().addStep( step )

	def buildAndReturn( self, configurations = [] ):
		"""BuildAndReturn executes the build and returns the exit code of the script.
		It is useful for scripts that need to perform other code after the build method.
		build wraps this function and exits with the error code.
		The method does not always return, though, only in build mode."""
		# enable and disable the steps according to the settings for the build mode
		# FIXME
		# ignore configurations for now
		try:
			self.getTimeKeeper().start()
			[ plugin.preFlightCheck( self ) for plugin in self.getPlugins() ]
			self.setup()
			[ plugin.setup( self ) for plugin in self.getPlugins() ]
			if self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Build:
				self.getExecutomat().run( self )
			elif self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Query:
				self.queryAndExit()
			elif self.getSettings().get( Settings.ScriptRunMode ) == Settings.RunMode_Print:
				self.printAndExit()
			else:
				assert self.getSettings().get( Settings.ScriptRunMode ) not in Settings.RunModes
				raise MomError( 'Unknown run mode "{0}". Known run modes are: {1}'.format( 
						self.getSettings().get( Settings.ScriptRunMode ),
						', '.join( Settings.RunModes ) ) )
			self.getTimeKeeper().stop()
			[ plugin.wrapUp( self ) for plugin in self.getPlugins() ]
			return self.getReturnCode()
		except MomException as e:
			self.message( self, 'Error during build, return code {0}: {1}'.format( e.getReturnCode() , str( e ) ) )
			return e.getReturnCode()
		except KeyboardInterrupt:
			self.message( self, 'Interrupted. Have a nice day.' )
			return InterruptedException( '' ).getReturnCode()
		finally:
			for plugin in self.getPlugins():
				try:
					plugin.shutDown( self )
				except Exception as e:
					text = '''\
An error occurred during shutdown: "{0}"
Offending module: "{1}" 
This error will not change the return code of the script!'''.format( str( e ), plugin.getName() )
					self.message( self, text )

	def build( self, configurations = [] ):
		"""build executes the build and exits the process with the correct return code."""
		sys.exit( self.buildAndReturn( configurations ) )

	def queryAndExit( self ):
		try:
			args = self.getParameters()._getArgs()[2:] # filter script name, 'query'
			settings = self.getSettings().getSettings()
			if args:
				for key in args:
					if key in settings:
						print( '{0}: {1}'.format( key, settings[key] ) )
					else:
						raise MomError( 'Undefind setting "{0}"'.format( key ) )
			else:
				# print all
				for key in settings:
					print( '{0}: {1}'.format( key, settings[key] ) )
			sys.exit( 0 )
		except Exception as e:
			print( 'Error: {0}'.format( str( e ) ) )
			sys.exit( 1 )

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

