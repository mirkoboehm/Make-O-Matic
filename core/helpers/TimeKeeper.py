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
import time

def formatted_time( datetimeObj ):
	try:
		text = time.strftime( "%a, %d %b %Y %H:%M:%S +0000" )
	except Exception:
		text = datetimeObj
	return text

def formatted_time_delta( timeDelta ):
	return formatted_duration( timeDelta.seconds + 60 * 60 * 24 * timeDelta.days )

def formatted_duration( noOfSeconds ):
	"""Returns a printable string that contains the duration in readable format"""
	# static definitions: 
	second = 1
	minute = 60 * second
	hour = 60 * minute
	day = 24 * hour
	# make the string: 
	days = int( noOfSeconds / day )
	hours = int( noOfSeconds / hour ) % 24
	minutes = int( noOfSeconds / minute ) % 60
	seconds = noOfSeconds % 60

	text = ''
	if days > 0:
		text += str( days ) + 'd '
	if hours > 0:
		text += str( hours ) + 'h '
	if minutes > 0:
		text += str( minutes ) + 'min '
	text += str( seconds )
	if seconds == 1:
		text += 'sec'
	else:
		text += 'secs'
	if not text:
		text = '---'
	return text

class TimeKeeper( object ):
	'''TimeKeeper records the time an operation took.'''

	def __init__( self ):
		'''	Constructor'''
		self.__startTime = None
		self.__stopTime = None

	def __enter__( self ):
		self.start()

	def __exit__( self, type, value, traceback ):
		self.stop()

	def start( self ):
		self.__startTime = datetime.utcnow()

	def getStartTime( self ):
		return self.__startTime

	def stop( self ):
		self.__stopTime = datetime.utcnow()

	def getStopTime( self ):
		return self.__stopTime

	def delta( self ):
		if not self.getStartTime() or not self.getStopTime():
			return 0
		return self.getStopTime() - self.getStartTime()

	def deltaString( self ):
		if not self.getStartTime() or not self.getStopTime():
			return '---'
		return formatted_time_delta( self.delta() )

