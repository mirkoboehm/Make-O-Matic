# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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

import os.path
from core.Exceptions import ConfigurationError, MomError
from core.helpers.GlobalMApp import mApp
from core.MObject import MObject

try:
	from lxml import etree
except ImportError:
	raise MomError( "Fatal: lxml package missing, required for Xml transformations" )

class XmlReportConverter( MObject ):

	TO_HTML = "xmlreport2html.xsl"

	def __init__( self, xmlReport ):
		MObject.__init__( self )

		self.__xml = etree.fromstring( xmlReport.getReport() )

		self.__xslTransformations = {}
		self.__registeredPlugins = []

		# init HTML converter
		f = open( os.path.dirname( __file__ ) + '/xslt/{0}'.format( self.TO_HTML ) )
		self.__xslTransformations[self.TO_HTML] = etree.XML( f.read() )

		self._fetchXsltTemplates( mApp() )

	def _convertTo( self, destinationFormat ):
		transform = etree.XSLT( self.__xslTransformations[destinationFormat] )
		return str( transform( self.__xml ) )

	def _fetchXsltTemplates( self, instructions ):
		for plugin in instructions.getPlugins():
			# prevent infinite loop on circular plugin dependencies
			if plugin in self.__registeredPlugins:
				mApp().debug( self, "XSLT template already added for plugin {0}".format( plugin.getName() ) )
				continue

			self.__registeredPlugins.append( plugin )
			self._addXsltTemplate( plugin, plugin.getXsltTemplate() )

			self._fetchXsltTemplates( plugin.getInstructions() ) # enter recursion

	def _addXsltTemplate( self, plugin, xslString ):
		if xslString is None :
			return

		# search for place to register new plugin templates
		pluginTemplate = self.__xslTransformations[self.TO_HTML].find( ".//{http://www.w3.org/1999/XSL/Transform}template[@match='plugin']" )
		placeholder = pluginTemplate.find( "{http://www.w3.org/1999/XSL/Transform}choose" )

		# validate XML
		try:
			element = etree.XML( """<xsl:when xmlns:xsl="http://www.w3.org/1999/XSL/Transform"	
				 xmlns="http://www.w3.org/1999/xhtml"
				 test="@name = '{0}'">{1}</xsl:when>""".format( plugin.getName(), xslString ) )
		except etree.XMLSyntaxError:
			raise ConfigurationError( "XSL template of {0} plugin malformed.".format( plugin.getName() ) )

		# insert new switch case
		placeholder.insert( 0, element )

	def convertToHtml( self ):
		return self._convertTo( self.TO_HTML )
