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

class MObject( object ):
	"""MObject is the base class for objects used during a MoM script run."""

	def __init__( self, name = None, type = "object" ):
		"""Constructor"""
		if name == None:
			name = self.__class__.__name__

		self.setName( name )
		self.setType( type )

	def setName( self, name ):
		# FIXME check for string
		self.__name = name

	def getName( self ):
		return self.__name

	def setType( self, type ):
		if type == None or len( type ) == 0:
			type = "object"

		self.__type = type

	def getType( self ):
		return self.__type

	def describe( self, prefix ):
		name = self.getName()
		clazz = self.__class__.__name__
		if name != clazz:
			print( '{0}{1}: {2}'.format( prefix, clazz, name ) )
		else:
			print( '{0}{1}'.format( prefix, clazz ) )

	def createXmlNode( self, document ):
		node = document.createElement( self.getType() )
		node.attributes["name"] = self.getName()

		return node
