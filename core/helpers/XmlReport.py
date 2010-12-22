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

from core.Instructions import Instructions
import traceback
from core.helpers.XmlUtils import create_exception_xml_node
from core.helpers.GlobalMApp import mApp
import xml.dom.minidom

class XmlReport( object ):
	"""Represents an report of the current build

	\see Plugin for more information about extending the default report output"""

	def __init__( self, instructions ):
		assert isinstance( instructions, Instructions )
		self.__instructions = instructions
		self.__doc = xml.dom.minidom.Document()

	def getReport( self ):
		return self.__doc.toxml()

	def prepare( self ):
		# fetch exception if any from mApp
		exception = mApp().getException()
		if exception:
			rootNode = mApp().createXmlNode( self.__doc, recursive = False )
			rootNode.appendChild( create_exception_xml_node( self.__doc, exception[0], exception[1] ) )
		else:
			try:
				rootNode = self._createNode( self.__instructions )
			except Exception as e:
				rootNode = mApp().createXmlNode( self.__doc, recursive = False )
				rootNode.appendChild( create_exception_xml_node( self.__doc, e, traceback.format_exc() ) )
		self.__doc.appendChild( rootNode )

	def _createNode( self, instructions ):
		"""Create XML node from Instructions object
		
		Also create nodes from children recursively"""

		node = instructions.createXmlNode( self.__doc )

		for child in instructions.getChildren():
			childNode = self._createNode( child ) # enter recursion
			node.appendChild( childNode )

		return node
