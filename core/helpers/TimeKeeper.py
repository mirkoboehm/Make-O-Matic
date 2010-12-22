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

from datetime import datetime, timedelta
from core.helpers.TimeUtils import formatted_time_delta

class TimeKeeper( object ):
	'''TimeKeeper records the time an operation took.'''

	def __init__( self ):
		self.__duration = timedelta( 0 )
		self.__startTime = None

	def __enter__( self ):
		self.start()

	def __exit__( self, type, value, traceback ):
		self.stop()

	def start( self ):
		self.__startTime = datetime.utcnow()

	def stop( self ):
		assert self.__startTime
		delta = datetime.utcnow() - self.__startTime
		self.__startTime = None
		self.__duration += delta

	def delta( self ):
		return self.__duration

	def deltaString( self ):
		if self.__duration == None:
			return '---'
		return formatted_time_delta( self.delta() )
