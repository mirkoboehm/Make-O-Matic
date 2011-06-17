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
import string
from core.Exceptions import MomException
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none
from core.helpers.XmlUtils import create_child_node
import inspect

class MObject( object ):
	"""MObject is the base class for objects used during a MoM script run."""

	def __init__( self, name = None ):
		if name == None:
			name = self.__class__.__name__
		self.setName( name )
		self.setObjectStatus( None )
		self.setObjectDescription( None )

	def setName( self, name ):
		# FIXME check for string
		self.__name = name

	def getName( self ):
		return self.__name

	def setObjectStatus( self, status ):
		'''The status is a short string message about the status of the object.
		The status is used in reports and in describe output. If it is None, it will be ignored.'''
		check_for_nonempty_string_or_none( status, 'The object status needs to be a string or None!' )
		self.__status = status

	def getObjectStatus( self ):
		return self.__status

	def setObjectDescription( self, description ):
		'''The description is a more detailed message about the object.
		The description is used in reports and in describe output. If it is None, it will be ignored.'''
		check_for_nonempty_string_or_none( description, 'The object status needs to be a string or None!' )
		self.__description = description

	def getObjectDescription( self ):
		return self.__description

	def getTagName( self ):
		return self.__class__.__name__.lower()

	def describe( self, prefix, details = None, replacePatterns = True ):
		"""Describe this object
		Print out information like class name"""
		status = ', '.join( filter( lambda x: x, [ details, self.getObjectStatus() ] ) )
		self._printDescribeLine( prefix, self.getName(), status, replacePatterns )
		if self.getObjectDescription():
			# FIXME (Mirko) find a better formating for the details
			self._printDescribeLine( prefix + ' > ', self.getName(), self.getObjectDescription(), replacePatterns )

	@classmethod
	def getBaseClassNames( cls ):
		return [c.__module__ + "." + c.__name__ for c in inspect.getmro( cls )]

	def _printDescribeLine( self, prefix, name, details, replacePatterns = True ):
		clazz = self.__class__.__name__
		if name != clazz:
			name = '{0} ({1})'.format( name, clazz )
		elements = [ name ]
		if details:
			elements += [ details.strip() ]
		text = ': '.join( elements )
		line = '{0}{1}'.format( prefix, text )

		# FIXME this is duplicated form ConsoleLogger, maybe it could use a helper?
		if replacePatterns:
			try:
				from core.helpers.GlobalMApp import mApp
				basedir = mApp().getBaseDir()
				line = string.replace( line, basedir, '$BASE' )
			except MomException:
				pass # no base directory set yet

		print( line )


	def getRelativeLinkTarget( self ):
		return ( None, None )

	def createXmlNode( self, document, recursive = True ):
		"""Create XML node for this object
		
		Feel free to overwrite in subclasses to add more details"""

		node = document.createElement( self.getTagName() )
		node.attributes["name"] = self.getName()
		node.attributes["bases"] = " ".join( self.getBaseClassNames() )
		node.attributes["relativeLinkTarget"] = str ( self.getRelativeLinkTarget()[0] )
		node.attributes["relativeLinkTargetDescription"] = str ( self.getRelativeLinkTarget()[1] )
		create_child_node( document, node, "objectdescription", self.getObjectDescription() if self.getObjectDescription() else "" )
		create_child_node( document, node, "objectstatus", self.getObjectStatus() if self.getObjectStatus() else "" )

		return node
