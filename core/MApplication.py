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
import sys
from core.loggers.Logger import Logger
from core.Exceptions import MomError, MomException, InterruptedException
from core.Settings import Settings
from core.helpers.TypeCheckers import check_for_nonnegative_int, check_for_nonempty_string
from core.Instructions import Instructions
import traceback

class MApplication( Instructions ):
	'''MApplication represents the facilities provided by the currently running script.
	It contains the loggers and reporters, for example. It also maintains the settings,
	and defines the exit code of the program.'''

	instance = None

	def __init__( self, minimumMomVersion = None, name = None, parent = None ):
		Instructions.__init__( self, name, parent )

		if MApplication.instance:
			raise MomError( 'The script tried to create more than one MApplication object!' )
		MApplication.instance = self

		self.__loggers = []
		self.__settings = Settings()
		self.__exception = None
		self.__returnCode = 0

		self._checkMinimumMomVersion( minimumMomVersion )

	def getMomVersion( self ):
		return self.getSettings().get( Settings.MomVersionNumber )

	def _checkMinimumMomVersion( self, minimumMomVersion ):
		'''Check if this make-o-matic copy is recent enough for this build script.

		If not, the function does not return, but instead exits the script with an error Message.'''

		if not minimumMomVersion:
			self.debug( self, 'No minimum make-o-matic version specified.' )
			return
		try:
			check_for_nonempty_string( minimumMomVersion, 'minimumMomVersion needs to be a version string like "0.5.5"' )
			minVersion = minimumMomVersion.split( '.' )
			version = self.getMomVersion().split( '.' )
			if len( version ) != 3 or len( minVersion ) != len( version ) :
				raise MomError( 'Version descriptions must be strings of 3 integer numbers, like "0.5.5"' )
			for position in range( len( version ) ):
				try:
					element = int( version[position] )
					minElement = int( minVersion[position] )
					if element < minElement:
						raise MomError( 'This build script requires make-o-matic ' + minimumMomVersion
											 + ', but this is only make-o-matic ' + self.getMomVersion() + ', aborting.' )
				except ValueError:
					raise MomError( 'Version descriptions must be strings of integer numbers, like "0.5.5"' )
		except MomException as  e:
			self.message( self, e.value )
			sys.exit( 1 )

	def addLogger( self, logger ):
		if not isinstance( logger, Logger ):
			raise MomError( 'Loggers need to re-implement the Logger class!' )
		self.__loggers.append( logger )
		self.addPlugin( logger )

	def getLoggers( self ):
		return self.__loggers

	def getSettings( self ):
		return self.__settings

	def registerReturnCode( self, code ):
		check_for_nonnegative_int( code, "The return code of the build script has to be a non-negative integer number!" )
		if self.__returnCode == 0:
			# only if there was no previous error:
			self.__returnCode = code
		else:
			self.debugN( self, 3, 'new return code {0} ignored, return code is already set to {1}.'
						.format( code, self.getReturnCode() ) )

	def getReturnCode( self ):
		return self.__returnCode

	def setException( self, exception ):
		self.__exception = exception

	def getException( self ):
		return self.__exception

	def message( self, mobject, text ):
		[ logger.message( self, mobject, text ) for logger in self.getLoggers() ]

	def debug( self, mobject, text ):
		[ logger.debug( self, mobject, text ) for logger in self.getLoggers() ]

	def debugN( self, mobject, level, text ):
		[ logger.debugN( self, mobject, level, text ) for logger in self.getLoggers() ]

	def run( self ):
		self.debugN( self, 2, 'executing' )
		try:
			self.execute()
			[ child.execute() for child in self.getChildren() ]
		finally:
			self.runWrapups()

	def querySettings( self, names = None ):
		try:
			settings = self.getSettings().getSettings()
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
			self.registerReturnCode( 1 )

	def _buildAndReturn( self ):
		'''Helper method that can be overloaded.'''
		try:
			self.runPreFlightChecks()
			self.runSetups()
			self.run()
		except MomException as e:
			self.registerReturnCode( e.getReturnCode() )
			self.setException( ( e, traceback.format_exc() ) )
			raise # rethrow exception
		finally:
			self.runShutDowns()

	def buildAndReturn( self ):
		'''buildAndReturn executes the build and returns the exit code of the script.
		It is useful for scripts that need to perform other code after the build method.
		build wraps this function and exits with the error code.
		The method does always return, though, if a MomException is caught. Any exception
		that does not inherit MomException will pass. '''
		try:
			self._buildAndReturn()
			self.message( self, 'Returning, return code {0}'.format( self.getReturnCode() ) )
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
