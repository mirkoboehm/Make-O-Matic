# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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

import xml.dom.minidom
from core.Instructions import Instructions

class XmlReport( object ):

	def __init__( self, instructions ):
		assert isinstance( instructions, Instructions )
		self.__instructions = instructions
		self.__doc = xml.dom.minidom.Document()

	def getReport( self ):
		return self.__doc.toxml()

	def prepare( self ):
		self.__doc.appendChild( self._createNode( self.__instructions ) )

	def _createNode( self, instructions ):
		"""Create XML node from Instructions object
		
		Also create nodes from children recursively"""

		node = instructions.createXmlNode( self.__doc )

		for child in instructions.getChildren():
			childNode = self._createNode( child ) # enter recursion
			node.appendChild( childNode )

		return node
