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
import sys, re
from core.loggers.Logger import Logger
from core.helpers.TypeCheckers import check_for_nonnegative_int
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.Exceptions import MomException

class ConsoleLogger( Logger ):
	"""ConsoleLogger prints status and debug messages to the stderr stream."""

	def __init__( self ):
		"""Constructor"""
		Logger.__init__( self, self.__class__.__name__ )

	def __getLevel( self, mapp ):
		verbosity = mapp.getSettings().get( Settings.ScriptLogLevel )
		check_for_nonnegative_int( verbosity, "The debug level needs to be an integer of zero or more" )
		return verbosity

	def message( self, mapp, mobject, msg ):
		text = str( msg )
		# FIXME this should be configurable somewhere, and preferably not only for the ConsoleLogger
		try:
			basedir = mApp().getBaseDir()
			text = re.sub( basedir, '$BASE', text )
		except MomException:
			pass # no base directory set yet		
		if not text.endswith( '\n' ): text = text + '\n'
		fulltext = '{0} {1}[{2}] {3}'.format( self.timeStampPrefix(), self.messagePrefix(), mobject.getName(), text )
		sys.stderr.write( fulltext )

	def debug( self, mapp, mobject, msg ):
		text = str( msg )
		if self.__getLevel( mapp ) > 0:
			self.message( mapp, mobject, 'DEBUG: ' + str( text ) )

	def debugN( self, mapp, mobject, level , msg ):
		check_for_nonnegative_int( level, "The debug level needs to be an integer of zero or more" )
		verbosity = self.__getLevel( mapp )
		if verbosity >= level:
			self.debug( mapp, mobject, msg )

	def preFlightCheck( self ):
		level = mApp().getSettings().get( Settings.ScriptLogLevel, True )
		check_for_nonnegative_int( level, 'The debug level must be a non-negative integer!' )
		if level > 0:
			mApp().debug( self, 'debug level is {0}'.format( level ) )
