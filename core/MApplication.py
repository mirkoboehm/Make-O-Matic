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
from core.loggers.Logger import Logger
from core.Exceptions import MomError, AbstractMethodCalledError, MomException, InterruptedException
from core.helpers.VersionChecker import checkMinimumMomVersion
from core.Settings import Settings
import sys
from core.helpers.TypeCheckers import check_for_nonnegative_int
from core.Instructions import Instructions

def mApp():
	if not MApplication._instance:
		raise MomError( 'mApp may only be called after the MApplication object has been created!' )
	return MApplication._instance

class MApplication( Instructions ):
	'''MApplication represents the facilities provided by the currently running script.
	It contains the loggers and reporters, for example. It also maintains the settings,
	and defines the exit code of the program.'''

	_instance = None

	def __init__( self, name = None, minimumMomVersion = None ):
		Instructions.__init__( self, name )
		if MApplication._instance:
			raise MomError( 'The script tried to create more than one MApplication object!' )
		MApplication._instance = self
		self.__loggers = []
		self.__settings = Settings()
		self.__returnCode = 0
		checkMinimumMomVersion( self, minimumMomVersion )

	def getMomVersion( self ):
		return '0.5.0'

	def addLogger( self, logger ):
		if not isinstance( logger, Logger ):
			raise MomError( 'Loggers need to re-implement the Logger class!' )
		self.__loggers.append( logger )
		self.addPlugin( logger )

	def getLoggers( self ):
		return self.__loggers

	def getSettings( self ):
		return self.__settings

	def setReturnCode( self, code ):
		check_for_nonnegative_int( code, "The return code of the build script has to be a non-negative integer number!" )
		self.__returnCode = code

	def getReturnCode( self ):
		return self.__returnCode

	def message( self, mobject, text ):
		[ logger.message( self, mobject, text ) for logger in self.getLoggers() ]

	def debug( self, mobject, text ):
		[ logger.debug( self, mobject, text ) for logger in self.getLoggers() ]

	def debugN( self, mobject, level, text ):
		[ logger.debugN( self, mobject, level, text ) for logger in self.getLoggers() ]

	def run( self ):
		raise AbstractMethodCalledError()

	def querySettings( self, names = None ):
		try:
			settings = mApp().getSettings().getSettings()
			if names:
				for key in names:
					if key in settings:
						print( '{0}: {1}'.format( key, settings[key] ) )
					else:
						raise MomError( 'Undefined setting "{0}"'.format( key ) )
			else:
				# print all
				for key in settings:
					print( '{0}: {1}'.format( key, settings[key] ) )
		except Exception as e:
			print( 'Error: {0}'.format( str( e ) ) )
			self.setReturnCode( 1 )

	def buildAndReturn( self ):
		'''buildAndReturn executes the build and returns the exit code of the script.
		It is useful for scripts that need to perform other code after the build method.
		build wraps this function and exits with the error code.
		The method does always return, though, if a MomException is caught. Any exception
		that does not inherit MomException will pass. '''
		try:
			self.run()
			return self.getReturnCode()
		except MomException as e:
			self.message( self, 'Error, return code {0}: {1}'.format( e.getReturnCode() , str( e ) ) )
			return e.getReturnCode()
		except KeyboardInterrupt:
			self.message( self, 'Interrupted. Have a nice day.' )
			return InterruptedException( '' ).getReturnCode()

	def build( self ):
		'''build executes the program and exits the process with the correct return code.'''
		sys.exit( self.buildAndReturn() )
