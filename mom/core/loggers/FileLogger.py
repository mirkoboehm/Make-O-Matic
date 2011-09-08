# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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

from mom.core.Settings import Settings
from mom.core.helpers.GlobalMApp import mApp
from mom.core.loggers.ConsoleLogger import ConsoleLogger
import codecs
import os.path

class FileLogger( ConsoleLogger ):

	FILENAME = "console.out"

	def __init__( self, name = None ):
		super( FileLogger, self ).__init__( name )

		self.f = None
		self.cachedMessages = []

	def preFlightCheck( self ):
		# only use the file logger if we are in build mode
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode != Settings.RunMode_Build:
			self.setEnabled( False )

	def __del__( self ):
		if self.f:
			self.f.close()

	def isReady( self ):
		return ( self.f != None )

	def setup( self ):
		dir = self.getInstructions().getBaseDir()
		filePath = os.path.join( dir, self.FILENAME )
		self.f = codecs.open( filePath, 'w', encoding = "utf-8" )

		self._writeCachedMessages()

	def _writeCachedMessages( self ):
		# write initially saved buffer
		for line in self.cachedMessages:
			self.f.write( line )

		# reset
		self.cachedMessages = []

	def _write( self, str ):
		if self.isReady():
			self.f.write( str )
		else:
			self.cachedMessages.append( str )

	def getObjectStatus( self ):
		return "Log file: {0}".format( self.FILENAME )
