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

from core.helpers.TimeKeeper import TimeKeeper, formattedDuration
import time

class TimeMethodCall( object ):
	def __init__( self, m ):
		self.__m = m

	def __call__( self, *args ):
		try:
			# keeper.start()
			return self.__m( self, *args )
		finally:
			# keeper.stop()
			pass

def timeme( keeper ):
	'''timeme times the execution time of a function, using the time keeper passed as 
	the argument.'''
	def timekeeper_function_wrapper( f ):

		def timed_function_wrapper( *args, **kwargs ):
			try:
				keeper.start()
				return f( *args, **kwargs )
			finally:
				keeper.stop()

		timekeeper_function_wrapper.__name__ = f.__name__ + '__timed'
		return timed_function_wrapper

	return timekeeper_function_wrapper

# this is the time keeper object
keeper = TimeKeeper()

class Tester( object ):

	@TimeMethodCall
	def test( self, secs ):
		time.sleep( 5 )

@timeme( keeper )
def test2( secs ):
	time.sleep( secs )

# main
# t = Tester()
# t.test( 5 )
test2( 125 )
print( keeper.deltaString() )

