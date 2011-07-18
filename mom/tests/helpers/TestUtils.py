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

import types
from hashlib import md5

def replace_bound_method( instance, methodPointer, newMethodPointer ):
	"""Replaces the bound method of instance with newMethodPointer

	Raises an AttributeError if method does not exist in the first place

	\note This method ensures that no new methods are attached to a class or instance"""

	if callable( methodPointer ):
		f = types.MethodType( newMethodPointer, instance, instance.__class__ )
		instance.__dict__[ methodPointer.__name__ ] = f
	else:
		raise AttributeError( "Method is not callable" )

def md5sum( filename, buf_size = 8192 ):
	m = md5()
	# the with statement makes sure the file will be closed
	with open( filename ) as f:
		# We read the file in small chunk until EOF
		data = f.read( buf_size )
		while data:
			# We had data to the md5 hash
			m.update( data )
			data = f.read( buf_size )
	# We return the md5 hash in hexadecimal format
	return m.hexdigest()
