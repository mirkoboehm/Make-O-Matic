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
from core.loggers.ConsoleLogger import ConsoleLogger
from core.helpers.TypeCheckers import check_for_nonnegative_int

"""A Project represents an entity to build. 
FIXME documentation
"""
class Project( MObject ):

	def __init__( self, projectName, minimalMomVersion = None ):
		"""Set up the build steps, parse the command line arguments."""
		MObject.__init__( self, projectName )
		self.__loggers = [ ConsoleLogger() ]
		self.__startTime = datetime.datetime.utcnow()
		self.__buildMode = 'm'
		self.__plugins = [ FolderManager() ]
		self.__returnCode = 0

	def getPlugins( self ):
		return self.__plugins

	def addPlugin( self, plugin ):
		self.__plugins.append( plugin )

	def getLoggers( self ):
		return self.__loggers

	def setReturnCode( self, code ):
		check_for_nonnegative_int( code, "The return code of the build script has to be a non-negative integer number!" )
		self.__returnCode = code

	def getReturnCode( self ):
		return self.__returnCode

	def message( self, text ):
		[ logger.message( text ) for logger in self.getLoggers() ]

	def debug( self, text ):
		[ logger.debug( text ) for logger in self.getLoggers() ]

	def debugN( self, level, text ):
		[ logger.debugN( level, text ) for logger in self.getLoggers() ]

	def build( self, configurations = [] ):
		# ignore configurations for now
		[ plugin.preFlightCheck( self ) for plugin in self.getPlugins() ]

