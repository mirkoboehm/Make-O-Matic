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
from textwrap import TextWrapper

try:
	from lxml import etree
except ImportError:
	raise MomError( "Fatal: lxml package missing, required for Xml transformations" )

class MyTextWrapper( TextWrapper ):
	"""TextWrapper Wrapper class ;)
	
	Provides easy access to indent and dedent methods"""

	MY_INDENT = " "

	def indent( self ):
		self.initial_indent = self.subsequent_indent = self.initial_indent + self.MY_INDENT

	def dedent( self ):
		self.initial_indent = self.subsequent_indent = self.initial_indent[:-len( self.MY_INDENT )]

class XmlReportConverter( MObject ):
	"""Converts a XmlReport instance to HTML, plain text and maybe others"""

	XSL_STYLESHEETS = {
		"html" : "xmlreport2html.xsl",
	}

	def __init__( self, xmlReport ):
		MObject.__init__( self )

		self.__xml = etree.fromstring( xmlReport.getReport() )

		self.__xslTemplateSnippets = {}
		self.__xmlTemplateFunctions = {}
		self.__registeredPlugins = []

		# load stylesheets from XSL_STYLESHEETS into memory
		for key, value in self.XSL_STYLESHEETS.items():
			f = open( os.path.dirname( __file__ ) + '/xslt/{0}'.format( value ) )
			self.__xslTemplateSnippets[key] = etree.XML( f.read() )

		self._fetchTemplates( mApp() )

	def _convertTo( self, destinationFormat ):
		"""Converts the report to destinationFormat, which is one of the keys in XSL_STYLESHEETS"""

		transform = etree.XSLT( self.__xslTemplateSnippets[destinationFormat] )
		return str( transform( self.__xml ) )

	def _fetchTemplates( self, instructions ):
		"""Fetches templates from all registered plugins in the Instruction object
		
		Loops through all plugins from this object and its children recursively."""

		for plugin in instructions.getPlugins():
			# prevent infinite loop on circular plugin dependencies
			if plugin in self.__registeredPlugins:
				mApp().debug( self, "XSLT template already added for plugin {0}".format( plugin.getName() ) )
				continue

			self.__registeredPlugins.append( plugin )

			self._addXslTemplate( plugin )
			self._addXmlTemplate( plugin )

		for child in instructions.getChildren():
			self._fetchTemplates( child ) # enter recursion

	def _addXslTemplate( self, plugin ):
		"""Adds the XSL template to stylesheet if plugin provides one
		
		Merges templates from plugins into the stylesheets provided by XSL_STYLESHEETS."""

		# iterate trough the dict from getXslTemplates(), add each template to the corresponding stylesheet
		for conversionType, markup in plugin.getXslTemplates().items():
			if not conversionType in self.__xslTemplateSnippets.keys():
				continue # invalid key, no stylesheet registered for that type of XSL

			# search for place to register new plugin templates
			stylesheet = self.__xslTemplateSnippets[conversionType]
			pluginTemplate = stylesheet.find( ".//{http://www.w3.org/1999/XSL/Transform}template[@match='plugin']" )
			placeholder = pluginTemplate.find( "{http://www.w3.org/1999/XSL/Transform}choose" )

			# create new element with markup provided from plugin
			try:
				element = etree.XML( """<xsl:when xmlns:xsl="http://www.w3.org/1999/XSL/Transform"	
					 xmlns="http://www.w3.org/1999/xhtml"
					 test="@name = '{0}'">{1}</xsl:when>""".format( plugin.getName(), markup ) )
			except etree.XMLSyntaxError:
				raise ConfigurationError( "XSL template of {0} plugin malformed.".format( plugin.getName() ) )

			# insert new element in the placeholder from the stylesheet
			placeholder.insert( 0, element )

	def _addXmlTemplate( self, plugin ):
		"""Adds lxml conversion code if plugin provides one
		
		Adds function pointers to the Plugin.getXmlTemplate() methods so that their parameter list can be evaluated when actually 
		parsing the tree"""

		# check if this plugin overwrites the getXmlTemplate method
		classMembers = plugin.__class__.__dict__.keys()
		if 'getXmlTemplate' not in classMembers:
			return # getXmlTemplate has not been overwritten, do not add function pointer

		functionPointer = plugin.getXmlTemplate
		self.__xmlTemplateFunctions[plugin.getName()] = functionPointer

	def convertToHtml( self ):
		"""Convenience method for converting the report to HTML using the protected _convertTo() method"""

		return self._convertTo( "html" )

	def convertToText( self ):
		"""Convenience method for converting the report to plain text using the recursive _toText() method"""

		wrapper = MyTextWrapper( drop_whitespace = False, width = 80 )

		return "\n".join( self._toText( self.__xml, wrapper ) )

	def _toText( self, element, wrapper ):
		"""Recursive method for parsing an ElementTree and converting it to plain text"""

		out = []

		if element.tag == "build":
			out += " "
			out += wrapper.wrap( "Build: {0}".format( element.attrib["name"] ) )
			out += " " # new line
			wrapper.indent()
			out += wrapper.wrap( "Platform:     {0} ({1})".format( element.attrib["sys-platform"], element.attrib["sys-version"] ) )
			out += wrapper.wrap( "Architecture: {0}".format( element.attrib["sys-architecture"] ) )
			out += wrapper.wrap( "Node name:    {0}".format( element.attrib["sys-nodename"] ) )
			wrapper.dedent()

		elif element.tag == "project":
			out += " "
			out += wrapper.wrap( "Project: {0}".format( element.attrib["name"] ) )
			out += " "
			wrapper.indent()
			out += wrapper.wrap( "Base directory: {0}".format( element.attrib["basedir"] ) )
			out += " "
			out += wrapper.wrap( "Start time (UTC): {0}".format( element.attrib["starttime"] ) )
			out += wrapper.wrap( "Stop time (UTC):  {0}".format( element.attrib["stoptime"] ) )
			out += " "
			out += wrapper.wrap( "Build time: {0}".format( element.attrib["timing"] ) )
			wrapper.dedent()

		elif element.tag == "plugins": # container element
			if len( element.getchildren() ) > 0:
				out += " "
				out += wrapper.wrap( "Plugins:" )

		elif element.tag == "plugin":
			name = element.attrib["name"]

			out += wrapper.wrap( "Plugin: {0}".format( element.attrib["name"] ) )

			if name in self.__xmlTemplateFunctions:
				wrapper.indent()
				try:
					out += self.__xmlTemplateFunctions[name]( element, wrapper )
				except AttributeError:
					mApp().debug( self, "Exception in getXmlTemplate function for plugin {0}".format( name ) )
				wrapper.dedent()

		elif element.tag == "configuration":
			out += " "
			out += wrapper.wrap( "Configuration: {0}".format( element.attrib["name"] ) )

		elif element.tag == "environment":
			out += " "
			out += wrapper.wrap( "Environment: {0}".format( element.attrib["name"] ) )

		elif element.tag == "steps": # container element
			if len( element.getchildren() ) > 0:
				out += " "
				out += wrapper.wrap( "Steps:" )

		elif element.tag == "step":
			if element.attrib["isEmpty"] == "True":
				return out # do not show empty step

			if element.attrib["isEnabled"] == "False":
				status = "disabled"
			elif element.attrib["isEmpty"] == "True":
				status = "noaction"
			elif element.attrib["failed"] == "True":
				status = "!failed!"
			else:
				status = "success "

			out += wrapper.wrap( '{0}: Step "{1}" (took {2})'.format( 
				status,
				element.attrib["name"] ,
				element.attrib["timing"]
			) )

			if element.attrib["failed"] == "False":
				return out # do not show children

#		elif element.tag == "action":
#			wrapper.subsequent_indent += " " * 10
#			out += wrapper.wrap( "Action: {0}".format( element.find( "logdescription" ).text ) )
#			out += wrapper.wrap( "  Code: {0}".format( element.attrib["returncode"] ) )

#		elif element.tag == "stderr":
#			if element.text:
#				originalIndent = wrapper.initial_indent
#				wrapper.initial_indent = wrapper.subsequent_indent = "> "
#				out += wrapper.wrap( "--- stderr output ---" )
#				out += wrapper.wrap( element.text )
#				out += wrapper.wrap( "--- end of stderr output ---" )
#				wrapper.initial_indent = wrapper.subsequent_indent = originalIndent # reset

		wrapper.indent()

		for childElement in element.getchildren():
			out += self._toText( childElement, wrapper ) # enter recursion

		wrapper.dedent()

		return out
