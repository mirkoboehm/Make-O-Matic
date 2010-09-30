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
from core.MObject import MObject
import os
from core.helpers.GlobalMApp import mApp
import re
from core.Exceptions import ConfigurationError
from core.helpers.EnvironmentVariables import add_to_path_collection
from core.helpers.TypeCheckers import check_for_nonempty_string, check_for_int

class Dependency( MObject ):
	'''Dependency represents a single installed dependency, and the adaptations to the environment variables needed to use it.'''

	_ControlFileName = 'MOM_PACKAGE_CONFIGURATION'
	_CommandPrefix = 'MOM_'

	def __init__( self, folder = None, name = None ):
		MObject.__init__( self, name )
		self.__commands = []
		self.setFolder( folder )
		self._setValid( False )
		self.setEnabled( False )
		self.setScore( 0 )
		self.__description = None

	def _getControlFileName( self, path ):
		return os.path.join( path, Dependency._ControlFileName )

	def setFolder( self, folder ):
		if folder:
			self.__folder = os.path.abspath( os.path.normpath( folder ) )
		else:
			self.__folder = None

	def getFolder( self ):
		return self.__folder

	def _setValid( self, onOff ):
		self.__valid = onOff

	def isValid( self ):
		return self.__valid

	def setEnabled( self, onOff ):
		self.__enabled = onOff

	def isEnabled( self ):
		return self.__enabled

	def setScore( self, score ):
		check_for_int( score, 'The package score must be an integer number.' )
		self.__score = int( score )

	def getScore( self ):
		return self.__score

	def _addCommand( self, line ):
		self.__commands.append( line )

	def getCommands( self ):
		return self.__commands

	def getContainingFolder( self ):
		pieces = os.path.split( self.getFolder() )
		return pieces[0]

	def _expandVariables( self, text ):
		# FIXME If there are no other supported variables, maybe remove the function. Or maybe not.
		result = text.replace( '$PWD', self.getFolder() )
		return result

	def _readControlFile( self, controlFile ):
		try:
			with open( controlFile, 'r' ) as inputFile:
				mApp().debugN( self, 3, 'loading settings from package control file "{0}"'.format( str ( controlFile ) ) )
				self._setValid( True )
				for line in inputFile.readlines():
					if re.match( '^\s*#', line ):
						continue # ignore comments
					if re.match( '^\s*$', line ):
						continue # ignore empty lines
					line = line.strip()
					if re.match( '^{0}'.format( Dependency._CommandPrefix ), line ):
						if not self.applyProperty( controlFile, line ):
							self._addCommand( line )
				return True
		except IOError:
			mApp().debugN( self, 3, 'no control file found at "{0}"'.format( controlFile ) )
			return False

	def applyProperty( self, controlFile, line ):
		enabledLine = re.match( '^({0}PACKAGE_ENABLED)\s+(\w+)$'.format( Dependency._CommandPrefix ), line )
		descriptionLine = re.match( '^({0}PACKAGE_DESCRIPTION)\s+(.+)$'.format( Dependency._CommandPrefix ), line )
		scoreLine = re.match( '^({0}PACKAGE_SCORE)\s+(.+)$'.format( Dependency._CommandPrefix ), line )
		# parse for "enabled" commands:
		try:
			if enabledLine:
				yesNo = str( enabledLine.group( 2 ) )
				if yesNo.lower() == 'false':
					self.setEnabled( False )
				elif yesNo.lower() == 'true':
					self.setEnabled( True )
				else:
					raise ConfigurationError( 'enable must be true or false' )
				mApp().debugN( self, 3, '>enabled< {0}'.format( str( self.isEnabled() ) ) )
				return True
			elif descriptionLine:
				description = str( descriptionLine.group( 2 ) )
				self._setDescription( description )
				mApp().debugN( self, 3, '>description< "{0}"'.format( self.getDescription() ) )
				return True
			elif scoreLine:
				score = str( scoreLine.group( 2 ) )
				self.setScore( score )
				mApp().debugN( self, 3, '>score< "{0}"'.format( self.getScore() ) )
				return True
			return False
		except ConfigurationError as value:
			mApp().message( self, 'error ({0}) in control file {1}\n--> {2}'.
				format( str( value ), controlFile, str( line ).strip() ) )
		except IndexError:
			mApp().message( self, 'syntax error in control file {0}\n--> {1}'.format( controlFile, str( line ).strip() ) )

	def applyCommand( self, line ):
		pass

	def apply( self ):
		assert self.getFolder()
		controlFile = self._getControlFileName( self.getFolder() )
		for line in self.getCommands():
			assert( not re.match( '^\s*#', line ) and not re.match( '^\s*$', line ) )
			export = re.match( '^({0}EXPORT)\s+(\w+)\s+(.+)$'.format( Dependency._CommandPrefix ), line )
			addTo = re.match( '^({0}ADD_PATH)\s+(\w+)\s+(\w+)\s+(.+)$'.format( Dependency._CommandPrefix ), line )
			enabled = re.match( '^({0}PACKAGE_ENABLED)\s+(\w+)$'.format( Dependency._CommandPrefix ), line )
			# parse commands:
			try:
				if export:
					variable = str( export.group( 2 ) )
					value = self._expandVariables( export.group( 3 ) )
					mApp().debugN( self, 4, 'setBuildEnvironment: >export< ' + variable + '="' + value + '"' )
					os.environ[variable] = value
				elif addTo:
					variable = str( addTo.group( 2 ) )
					mode = self._expandVariables( addTo.group( 3 ) )
					value = self._expandVariables( addTo.group( 4 ) )
					if mode == 'APPEND':
						mApp().debugN( self, 4, 'setBuildEnvironment: >append< ' + variable + ': "' + value + '"' )
						add_to_path_collection( variable, value, 'append' )
					elif mode == 'PREPEND':
						mApp().debugN( self, 4, 'setBuildEnvironment: >prepend< ' + variable + ': "' + value + '"' )
						add_to_path_collection( variable, value, 'prepend' )
					else:
						raise ConfigurationError( 'mode missing' )
				elif enabled:
					yesNo = str( enabled.group( 2 ) )
					if yesNo.lower() == 'false':
						enabled = False
					elif yesNo.lower() == 'true':
						enabled = True
					else:
						raise ConfigurationError( 'enable must be true or false' )
					mApp().debugN( self, 2, 'setBuildEnvironment: >enabled< ' + str( enabled ) )
				elif re.match( '^{0}'.format( Dependency._CommandPrefix ), line ):
					mApp().message( self, 'unknown command in control file for ' + controlFile + '\n--> ' + str( line ).strip() )
				else:
					mApp().message( self, 'parse error in control file for ' + controlFile + '\n--> ' + str( line ).strip() )
			except ConfigurationError as value:
				mApp().message( self, 'error (' + str( value ) + ') in control file for ' + controlFile + '\n--> ' + str( line ).strip() )
			except IndexError:
				mApp().message( self, 'syntax error in control file for ' + controlFile + '\n--> ' + str( line ).strip() )

	def verify( self ):
		'''Verify that the folder contains a MOM package control file. If so, evaluate it.'''
		if os.path.isdir( self.getFolder() ):
			self._readControlFile( self._getControlFileName( self.getFolder() ) )
			if self.isValid():
				if self.isEnabled():
					mApp().debugN( self, 4, '{0} is an enabled dependency'.format( str( self.getFolder() ) ) )
					return True
				else:
					mApp().debugN( self, 4, '{0} is a disabled dependency'.format( str( self.getFolder() ) ) )
					return False
			else:
				mApp().debugN( self, 5, '{0} is not a MOM dependency folder'.format( str( self.getFolder() ) ) )
				return False

	def _setDescription( self, description ):
		check_for_nonempty_string( description, 'A MOM Package Configuration description cannot be empty!' )
		self.__description = description

	def getDescription( self ):
		if not self.__description:
			name = os.path.split( self.getFolder() )[1]
			return name
		else:
			return self.__description

