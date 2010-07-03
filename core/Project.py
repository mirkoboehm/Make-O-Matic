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

import datetime
from core.MObject import MObject
from core.modules.FolderManager import FolderManager
from core.modules.SourceCodeProvider import SourceCodeProvider
from core.loggers.Logger import Logger
from core.helpers.TypeCheckers import check_for_nonnegative_int
from core.executomat.Executomat import Executomat
from core.executomat.Step import Step
from core.Settings import Settings
import sys
from core.Exceptions import InterruptedException, MomError

"""A Project represents an entity to build. 
FIXME documentation
"""
class Project( MObject ):

	def __init__( self, projectName, minimalMomVersion = None ):
		"""Set up the build steps, parse the command line arguments."""
		MObject.__init__( self, projectName )
		self.__settings = Settings()
		self.__scm = None
		self.__loggers = []
		self.__startTime = datetime.datetime.utcnow()
		self.__buildMode = 'm'
		self.__plugins = [ FolderManager() ]
		self.__returnCode = 0
		self.__executomat = Executomat( "Project Executomat" )

	def getSettings( self ):
		return self.__settings

	def setScm( self, scm ):
		if self.getScm():
			raise MomError( 'The master SCM can only be set once!' )
		if not isinstance( scm, SourceCodeProvider ):
			raise MomError( 'SCMs need to re-implement the SourceCodeProvider class!' )
		self.__scm = scm
		self.addPlugin( scm )

	def getScm( self ):
		return self.__scm

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

	def setReturnCode( self, code ):
		check_for_nonnegative_int( code, "The return code of the build script has to be a non-negative integer number!" )
		self.__returnCode = code

	def getReturnCode( self ):
		return self.__returnCode

	def getExecutomat( self ):
		return self.__executomat

	def message( self, mobject, text ):
		[ logger.message( mobject, text ) for logger in self.getLoggers() ]

	def debug( self, mobject, text ):
		[ logger.debug( mobject, text ) for logger in self.getLoggers() ]

	def debugN( self, mobject, level, text ):
		[ logger.debugN( mobject, level, text ) for logger in self.getLoggers() ]

	def setup( self ):
		for step in self.getSettings().getProjectBuildSteps():
			self.getExecutomat().addStep( Step( step ) )

	def buildAndReturn( self, configurations = [] ):
		"""BuildAndReturn executes the build and returns the exit code of the script.
		It is useful for scripts that need to perform other code after the build method.
		build wraps this function and exits with the error code."""
		# enable and disable the steps according to the settings for the build mode
		# FIXME
		# ignore configurations for now
		try:
			[ plugin.preFlightCheck( self ) for plugin in self.getPlugins() ]
			self.setup()
			[ plugin.setup( self ) for plugin in self.getPlugins() ]
			self.getExecutomat().run( self )
			[ plugin.wrapUp( self ) for plugin in self.getPlugins() ]
			return 0
		except KeyboardInterrupt:
			self.message( 'Interrupted. Have a nice day.' )
			return InterruptedException().getReturnCode()
		finally:
			[ plugin.shutDown( self ) for plugin in self.getPlugins() ]

	def build( self, configurations = [] ):
		"""build executes the build and exits the process with the correct return code."""
		sys.exit( self.buildAndReturn( configurations ) )
