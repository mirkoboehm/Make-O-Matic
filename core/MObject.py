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

class MObject( object ):
	"""MObject is the base class for objects used during a MoM script run."""

	def __init__( self, name = None, command = None ):
		"""Constructor"""

		if name == None:
			name = self.__class__.__name__

		self.setName( name )

	def setName( self, name ):
		# FIXME check for string
		self.__name = name

	def getName( self ):
		return self.__name

	def getTagName( self ):
		return self.__class__.__name__.lower()

	def describe( self, prefix ):
		"""Describe this object
		
		Print out information like class name"""

		name = self.getName()
		clazz = self.__class__.__name__
		if name != clazz:
			print( '{0}{1}: {2}'.format( prefix, clazz, name ) )
		else:
			print( '{0}{1}'.format( prefix, clazz ) )

	def createXmlNode( self, document ):
		"""Create XML node for this object
		
		Feel free to overwrite in subclasses to add more details"""

		node = document.createElement( self.getTagName() )
		node.attributes["name"] = self.getName()

		return node
