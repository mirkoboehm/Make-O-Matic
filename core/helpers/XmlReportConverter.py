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

try:
	from lxml import etree
except ImportError:
	raise MomError( "Fatal: lxml package missing, required for Xml transformations" )

class XmlReportConverter( object ):

	TO_HTML = "xmlreport2html.xsl"

	def __init__( self, xmlReport ):
		self.__project = xmlReport.getProject()
		self.__xml = etree.fromstring( xmlReport.getReport() )

		self.__xslTransformations = {}
		self.__registeredPlugins = []

		# init HTML converter
		f = open( os.path.dirname( __file__ ) + '/xslt/{0}'.format( self.TO_HTML ) )
		self.__xslTransformations[self.TO_HTML] = etree.XML( f.read() )

		# fetch XSL templates from external plugins/loggers
		for logger in self.__project.getBuild().getLoggers():
			self._addXsltTemplate( logger.getName(), logger.getXsltTemplate() )

		for plugin in self.__project.getPlugins():
			self._addXsltTemplate( plugin.getName(), plugin.getXsltTemplate() )

	def _convertTo( self, destinationFormat ):
		transform = etree.XSLT( self.__xslTransformations[destinationFormat] )
		return str( transform( self.__xml ) )

	def _addXsltTemplate( self, pluginName, xslString ):
		if xslString is None :
			return

		if pluginName in self.__registeredPlugins:
			mApp().debug( self, "XSLT template already added for plugin {0}".format( pluginName ) )
			return

		self.__registeredPlugins.append( pluginName )

		# search for place to register new plugin templates
		pluginTemplate = self.__xslTransformations[self.TO_HTML].find( ".//{http://www.w3.org/1999/XSL/Transform}template[@match='plugin']" )
		placeholder = pluginTemplate.find( "{http://www.w3.org/1999/XSL/Transform}choose" )

		# validate XML
		try:
			element = etree.XML( """<xsl:when xmlns:xsl="http://www.w3.org/1999/XSL/Transform"	
				 xmlns="http://www.w3.org/1999/xhtml"
				 test="@name = '{0}'">{1}</xsl:when>""".format( pluginName, xslString ) )
		except etree.XMLSyntaxError:
			raise ConfigurationError( "XSL template of {0} plugin malformed.".format( pluginName ) )

		# insert new switch case
		placeholder.insert( 0, element )

	def convertToHtml( self ):
		return self._convertTo( self.TO_HTML )
