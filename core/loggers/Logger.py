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

from __future__ import unicode_literals

from datetime import datetime
from core.Plugin import Plugin
from buildcontrol.SubprocessHelpers import get_debug_prefix

class Logger( Plugin ):
	"""Logger is the base class for Logger objects."""

	def __init__( self, name ):
		Plugin.__init__( self, name )

	def error( self, mapp, mobject, msg ):
		return self.logError( mapp, mobject, msg )

	def logError( self, mapp, mobject, msg ):
		raise NotImplementedError()

	def message( self, mapp, mobject, msg ):
		return self.logMessage( mapp, mobject, msg )

	def logMessage( self, mapp, mobject, msg ):
		raise NotImplementedError()

	def debug( self, mapp, mobject, msg ):
		return self.logDebug( mapp, mobject, msg )

	def logDebug( self, mapp, mobject, msg ):
		raise NotImplementedError()

	def debugN( self, mapp, mobject, level , msg ):
		return self.logDebugN( mapp, mobject, level, msg )

	def logDebugN( self, mapp, mobject, level , msg ):
		raise NotImplementedError()

	def timeStampPrefix( self ):
		return datetime.now().strftime( '%y%m%d-%H:%M:%S' )

	def messagePrefix( self ):
		return get_debug_prefix()
