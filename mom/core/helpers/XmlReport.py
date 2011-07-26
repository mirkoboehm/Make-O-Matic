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

from __future__ import unicode_literals

from core.Instructions import Instructions
import traceback
from core.helpers.XmlUtils import create_exception_xml_node
from core.helpers.GlobalMApp import mApp
import xml.dom.minidom

class XmlReportInterface( object ):

	def getReport( self ):
		"""\return String representing a valid Make-O-Matic XML report

		\note Be sure to call this *after* the build run has completed!"""

		raise NotImplementedError()

class StringBasedXmlReport( XmlReportInterface ):

	def __init__( self, xmlString ):
		self.__doc = xml.dom.minidom.parseString( xmlString )

	def getReport( self ):
		return self.__doc.toxml()

class InstructionsXmlReport( XmlReportInterface ):
	"""Represents an report of the current build

	\see Plugin for more information about extending the default report output"""

	REPORT_XML_VERSION = 1

	def __init__( self, instructions ):
		assert isinstance( instructions, Instructions )
		self.__instructions = instructions

	def getReport( self ):
		doc = xml.dom.minidom.Document()
		rootNode = self._createRootNode( doc )

		# fetch exception if any from mApp
		exception = mApp().getException()
		if exception:
			instructionsNode = mApp().createXmlNode( doc, recursive = False )
			tracebackToUnicode = u"".join( [x.decode( "utf-8" ) for x in exception[1] ] )
			instructionsNode.appendChild( create_exception_xml_node( doc, exception[0], tracebackToUnicode ) )
		else:
			try:
				instructionsNode = self._createNodesRecursively( self.__instructions, doc )
			except Exception as e:
				instructionsNode = mApp().createXmlNode( doc, recursive = False )
				exceptionNode = create_exception_xml_node(
						doc,
						"Caught exception during report generation: {0}".format( e ),
						traceback.format_exc()
				)
				instructionsNode.appendChild( exceptionNode )

		rootNode.appendChild( instructionsNode )
		doc.appendChild( rootNode )
		return doc.toxml()

	def _createRootNode( self, document ):
		rootNode = document.createElement( "mom-report" )
		rootNode.attributes["name"] = "Make-O-Matic report"
		rootNode.attributes["reportXmlVersion"] = str( self.REPORT_XML_VERSION )
		return rootNode

	def _createNodesRecursively( self, instructions, document ):
		"""Create XML node from Instructions object

		Also create nodes from children recursively"""

		node = instructions.createXmlNode( document )

		for child in instructions.getChildren():
			childNode = self._createNodesRecursively( child, document ) # enter recursion
			node.appendChild( childNode )

		return node
