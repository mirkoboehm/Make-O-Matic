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
from core.MObject import MObject
import os
from core.helpers.GlobalMApp import mApp
import re
from core.Exceptions import ConfigurationError

class Dependency( MObject ):
	'''Dependency represents a single installed dependency, and the adaptations to the environment variables needed to use it.'''

	_ControlFileName = 'MOM_PACKAGE_CONFIGURATION'

	def __init__( self, folder = None, name = None ):
		MObject.__init__( self, name )
		self.__commands = []
		self.setFolder( folder )
		self._setValid( False )
		self.setEnabled( False )

	def _getControlFileName( self, path ):
		return os.path.join( path, Dependency._ControlFileName )

	def _readControlFile( self, controlFile ):
		prefix = 'MOM_'
		try:
			with open ( controlFile, 'r' ) as input:
				mApp().debugN( self, 2, 'loading settings from package control file "{0}"'.format( str ( controlFile ) ) )
				self._setValid( True )
				for line in input.readlines():
					if re.match( '^\s*#', line ): continue # ignore comments
					if re.match( '^\s*$', line ): continue # ignore empty lines
					line = line.strip()
					enabledLine = re.match( '^({0}PACKAGE_ENABLED)\s+(\w+)$'.format( prefix ), line )
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
							mApp().debugN( self, 3, 'build environments: >enabled< {0}'.format( str( self.isEnabled() ) ) )
						else:
							if re.match( '^{0}'.format( prefix ), line ):
								self._addCommand( line )
					except ConfigurationError as value:
						mApp().message( 'error ({0}) in control file {1}\n--> {2}'.
							format( str( value ), controlFile, str( line ).strip() ) )
					except IndexError:
						mApp().message( 'syntax error in control file {0}\n--> {1}'.format( controlFile, str( line ).strip() ) )
		except IOError:
			mApp().debugN( self, 3, 'no control file found at "{0}"'.format( controlFile ) )

	def setFolder( self, folder ):
		self.__folder = os.path.abspath( os.path.normpath( folder ) )

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

	def _addCommand( self, line ):
		self.__commands.append( line )

	def getCommands( self ):
		return self.__commands

	def getContainingFolder( self ):
		pieces = os.path.split( self.getFolder() )
		return pieces[0]

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

	def getDescription( self ):
		name = os.path.split( self.getFolder() )[1]
		return name
