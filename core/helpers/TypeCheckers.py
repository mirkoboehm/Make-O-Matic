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
from core.Exceptions import ConfigurationError

def check_for_list_of_strings( expression, description ):
	if not isinstance( expression, list ):
		raise ConfigurationError( description )
	for obj in expression:
		if not isinstance( obj, str ):
			raise ConfigurationError( description )

def check_for_string( expression, description ):
	if not isinstance( expression, str ):
		raise ConfigurationError( description )

def check_for_nonempty_string( expression, description ):
	if not isinstance( expression, str ) or expression.isEmpty():
		raise ConfigurationError( description )

def check_for_int( expression, description ):
	try:
		int( expression )
	except ValueError:
		raise ConfigurationError( description )

def check_for_nonnegative_int( expression, description ):
	try:
		value = int( expression )
		if( value < 0 ):
			raise ConfigurationError( description )
	except ValueError:
		raise ConfigurationError( description )
