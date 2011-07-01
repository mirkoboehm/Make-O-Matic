# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2011 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Andreas Holzammer <andy@kdab.com>
# 
# Make-O-Matic is free software: you can redistribute it and/or modify
# it un>r the terms of the GNU General Public License as published by
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
from core.Plugin import Plugin
from core.Settings import Settings
from core.actions.filesystem.CopyActionBase import CopyActionBase
from core.helpers.GlobalMApp import mApp
from core.helpers.TemplateSupport import MomTemplate
from core.helpers.TypeCheckers import check_for_path_or_none, check_for_string, check_for_list_of_paths
from core.helpers.XmlReportConverter import ReportFormat
from urlparse import urljoin
import os

class PublisherAction( CopyActionBase ):

	def __init__( self, sourceLocation, targetLocation ):
		CopyActionBase.__init__( self,
								sourceLocation = sourceLocation,
								targetLocation = targetLocation )

		self.setExtraUploadSubDirs( [] )

	def setExtraUploadSubDirs( self, listOfSubdirs ):
		check_for_list_of_paths( listOfSubdirs, 'The list of extra upload subdirectories most contains paths.' )
		self.__extraUploadSubDirs = listOfSubdirs

	def getExtraUploadSubDirs( self ):
		return self.__extraUploadSubDirs

	def _getExtraUploadSubdirsAsString( self ):
		paths = map( str, self.getExtraUploadSubDirs() )
		return paths

class Publisher( Plugin ):

	def __init__( self, name = None, uploadLocation = None, localDir = None ):
		Plugin.__init__( self, name )

		self.setUploadBaseUrl( None )
		self.setUploadLocation( uploadLocation )
		self.setLocalDir( localDir )
		self._setStep( 'upload-packages' )
		self.setExtraUploadSubDirs( [] )

	def preFlightCheck( self ):
		if not self.getUploadLocation():
			raise ConfigurationError( "Must have a valid upload location!" )

		if not self.getUploadBaseUrl():
			raise ConfigurationError( "Must have a valid upload base URL!" )

	def getObjectStatus( self ):
		# self.getUploadUrl() may throw if revision, etc. is not available. Catch this.
		try:
			uploadUrl = self.getUploadUrl()
		except ConfigurationError:
			uploadUrl = "(Cannot yet resolve location)"

		return "Upload location: {0}".format( uploadUrl )

	def getPluginType( self ):
		return "publisher"

	def getXslTemplates( self ):
		return { ReportFormat.HTML:
			"""
			<a>
				<xsl:attribute name="href"><xsl:value-of select="@publisherUrl"/></xsl:attribute>
				Get full report here
			</a>
			""" }

	def createXmlNode( self, document ):
		node = Plugin.createXmlNode( self, document )
		node.attributes["publisherUrl"] = self.getUploadUrl()
		return node

	def setUploadLocation( self, location ):
		check_for_path_or_none( location, 'The upload location must be a nonempty string!' )
		self.__uploadLocation = location

	def getUploadLocation( self ):
		return self.__uploadLocation

	def setLocalDir( self, localDir ):
		check_for_path_or_none( localDir, 'The local directory must be a nonempty string!' )
		self.__localDir = localDir

	def getLocalDir( self ):
		return self.__localDir

	def _setStep( self, step ):
		check_for_string( step, 'The step for the publisher must be a string representing a step name!' )
		self.__step = step

	def getStep( self ):
		return self.__step

	def setExtraUploadSubDirs( self, listOfSubdirs ):
		check_for_list_of_paths( listOfSubdirs, 'The list of extra upload subdirectories most contains paths.' )
		self.__extraUploadSubDirs = listOfSubdirs

	def getExtraUploadSubDirs( self ):
		return self.__extraUploadSubDirs

	def _getExtraUploadSubdirsAsString( self ):
		paths = map( str, self.getExtraUploadSubDirs() )
		return paths

	def _getFullUploadLocation( self ):
		'''Create the full upload path from the location and the extra sub directories and return it.'''
		complete = os.path.join( self.getUploadLocation(), *self._getExtraUploadSubdirsAsString() )
		return complete

	def getUploadSubDirs( self ):
		subdirsTemplateString = mApp().getSettings().get( Settings.PublisherSubdirectoryTemplate, True )
		s = MomTemplate( subdirsTemplateString )
		ret = s.substitute( escape = True )
		return ret

	def setUploadBaseUrl( self, baseUrl ):
		self.__uploadBaseUrl = baseUrl

	def getUploadBaseUrl( self ):
		return self.__uploadBaseUrl

	def getUploadUrl( self ):
		subDirs = self.getUploadSubDirs()
		if subDirs:
			return urljoin( self.getUploadBaseUrl(), self.getUploadSubDirs() )

		return self.getUploadBaseUrl()
