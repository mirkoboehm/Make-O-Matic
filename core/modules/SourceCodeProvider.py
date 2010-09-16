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

from core.Exceptions import MomError
from core.helpers.TypeCheckers import check_for_path
from core.Plugin import Plugin

class SourceCodeProvider( Plugin ):

	def __init__( self, name = None ):
		"""Constructor"""
		Plugin.__init__( self, name )
		self.__url = None
		self.__revision = None

		self.__srcDir = None

	def getIdentifier( self ):
		raise NotImplementedError

	def setUrl( self, url ):
		self.__url = url

	def getUrl( self ):
		return self.__url

	def setSrcDir( self, srcDir ):
		check_for_path( srcDir, 'The course folder needs to be a non-empty string!' )
		self.__srcDir = srcDir

	def getSrcDir( self ):
		return self.__srcDir

	def setRevision( self, revision ):
		self.__revision = revision

	def getRevision( self ):
		return self.__revision

	def getRevisionInfo( self ):
		"""Returns a RevisionInfo object"""
		raise NotImplementedError

	def printRevisionsSince( self, options ):
		"""Print revisions committed since the specified revision."""
		if not options:
			raise MomError( 'No revision specified to start with!' )
		if len( options ) > 2:
			raise MomError( 'Error, extra options. Specify revision and optionally the maximum number of revisions to print.' )
		revision = options[0]
		cap = None
		if len( options ) == 2:
			cap = int( options[1] )

		revisions = self._getRevisionsSince( revision, cap )
		lines = []
		for revision in revisions:
			line = '{0} {1} {2}:{3}'.format( revision[0], revision[1], self.getIdentifier(), revision[2] )
			lines.append( line )
		return '\n'.join( lines )

	def _getRevisionsSince( self, revision, cap = None ):
		"""Return revisions committed since the specified revision."""
		raise NotImplementedError

	def printCurrentRevision( self, options ):
		"""Print current (most recent) revision."""
		if options:
			raise MomError( 'print current-revision does not understand any extra options!' )

		revision = self._getCurrentRevision()
		return revision

	def _getCurrentRevision( self ):
		'''Return the identifier of the current revisions.'''
		raise NotImplementedError

	def makeCheckoutStep( self ):
		"""Create steps to check out the source code"""
		raise NotImplementedError()

	def makeExportStep( self, targetDir ):
		"""Create a Step that will export the source code to the target directory."""
		raise NotImplementedError()

	def setup( self ):
		"""Setup is called after the build steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makeCheckoutStep()
		# FIXME it needs to be decided by the builder if this gets called!
		# self.makeExportStep( project )

	def getXslTemplates( self ):
		return { "html":
			"""
			Revision: <xsl:value-of select="@revision"/><br/>
			Committer: <xsl:value-of select="@committer"/><br/>
			Time: <xsl:value-of select="@commitTime"/><br/>
			Message: <xsl:value-of select="commitMessage"/>
			""" }

	def getXmlTemplate( self, element, wrapper ):
		return wrapper.wrap( "Revision: {0}".format( element.attrib["revision"] ) ) + \
			wrapper.wrap( "Committer: {0}".format( element.attrib["committer"] ) ) + \
			wrapper.wrap( "Time: {0}".format( element.attrib["commitTime"] ) ) + \
			wrapper.wrap( "Message: {0}".format( element.find( "commitMessage" ).text ) )

	def createXmlNode( self, document ):
		node = Plugin.createXmlNode( self, document )

		info = self.getRevisionInfo()
		node.attributes["revision"] = info.revision
		node.attributes["committer"] = info.committer
		node.attributes["commitTime"] = info.commitTime
		create_child_node( document, node, "commitMessage", info.commitMessage )

		return node


def create_child_node( document, parentNode, tagName, text ):
	elementNode = document.createElement( tagName )
	textNode = document.createTextNode( str( text ) )
	elementNode.appendChild( textNode )
	parentNode.appendChild( elementNode )
