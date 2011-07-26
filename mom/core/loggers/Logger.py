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
from datetime import datetime
from core.Plugin import Plugin
from buildcontrol.SubprocessHelpers import get_debug_prefix

class Logger( Plugin ):
	"""Logger is the base class for Logger objects."""

	def __init__( self, name ):
		Plugin.__init__( self, name )
		self.__cachedMessages = {}

	def error( self, mapp, mobject, msg, compareTo = None ):
		if not self._checkForDuplicateMessage( msg, compareTo ):
			return self._logError( mapp, mobject, msg )

	def _logError( self, mapp, mobject, msg ):
		raise NotImplementedError()

	def message( self, mapp, mobject, msg, compareTo = None ):
		if not self._checkForDuplicateMessage( msg, compareTo ):
			return self._logMessage( mapp, mobject, msg )

	def _logMessage( self, mapp, mobject, msg ):
		raise NotImplementedError()

	def debug( self, mapp, mobject, msg, compareTo = None ):
		if not self._checkForDuplicateMessage( msg, compareTo ):
			return self._logDebug( mapp, mobject, msg )

	def _logDebug( self, mapp, mobject, msg ):
		raise NotImplementedError()

	def debugN( self, mapp, mobject, level , msg, compareTo = None ):
		if not self._checkForDuplicateMessage( msg, compareTo ):
			return self._logDebugN( mapp, mobject, level, msg )

	def _logDebugN( self, mapp, mobject, level , msg ):
		raise NotImplementedError()

	def _timeStampPrefix( self ):
		return datetime.now().strftime( '%y%m%d-%H:%M:%S' )

	def _messagePrefix( self ):
		return get_debug_prefix()

	def _checkForDuplicateMessage( self, msg, compareTo ):
		if not compareTo:
			return False
		try:
			if self.__cachedMessages.has_key( msg ):
				if self.__cachedMessages[ msg ] == compareTo:
					return True
				else:
					return False
		finally:
			self.__cachedMessages[msg] = compareTo
