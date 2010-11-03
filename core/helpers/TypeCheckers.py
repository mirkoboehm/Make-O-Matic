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
from core.Exceptions import ConfigurationError

def check_for_list_of_paths( expression, description ):
	if not isinstance( expression, list ):
		raise ConfigurationError( description )
	for obj in expression:
		check_for_path( obj, description )

def check_for_list_of_strings( expression, description ):
	if not isinstance( expression, list ):
		raise ConfigurationError( description )
	for obj in expression:
		check_for_string( obj, expression )

def check_for_list_of_strings_or_none( expression, description ):
	if expression == None:
		return
	check_for_list_of_strings( expression, description )

def check_for_string( expression, description ):
	if not isinstance( expression, str ) and not isinstance( expression, unicode ):
		raise ConfigurationError( description )

def check_for_nonempty_string( expression, description ):
	if not expression:
		raise ConfigurationError( description )
	check_for_string( expression, description )

def check_for_nonempty_string_or_none( expression, description ):
	if expression == None:
		return
	check_for_nonempty_string( expression, description )

def check_for_path( expression, description ):
	# import locally, because PathResolver uses the type checkers as well
	from core.helpers.PathResolver import PathResolver
	if not isinstance( expression, PathResolver ):
		check_for_nonempty_string( expression, description )

def check_for_path_or_none( expression, description ):
	if expression:
		check_for_path( expression, description )

def check_for_int( expression, description, lessThan = None ):
	try:
		value = int( expression )
		if lessThan != None and value < lessThan:
			raise ConfigurationError( description )
	except ( ValueError, TypeError ):
		raise ConfigurationError( description )

def check_for_nonnegative_int( expression, description ):
	check_for_int( expression, description, 0 )

def check_for_positive_int( expression, description ):
	check_for_int( expression, description, 1 )

