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

import os.path
from core.Exceptions import ConfigurationError, MomError, returncode_to_description
from core.helpers.GlobalMApp import mApp
from core.MObject import MObject
from textwrap import TextWrapper
from core.helpers.XmlUtils import string_from_node_attribute, string_from_node, float_from_node_attribute
from datetime import datetime
from core.helpers.TimeKeeper import formatted_time_delta

try:
	from lxml import etree
except ImportError:
	raise MomError( "Fatal: lxml package missing, required for Xml transformations" )


class ReportFormat:
	"""Enum-like structure for output format"""

	XML = 0 # no conversion, default
	TEXT = 1
	HTML = 2

	@staticmethod
	def toString( reportFormat ):
		if reportFormat == 0:
			return "XML"
		elif reportFormat == 1:
			return "Plain text"
		elif reportFormat == 2:
			return "HTML"
		else:
			return "Unknown format"


class _MyTextWrapper( TextWrapper ):
	"""TextWrapper Wrapper class ;)
	
	Provides easy access to indent and dedent methods"""

	def indent( self, level = 1, indentString = " " ):
		self.initial_indent = self.subsequent_indent = self.initial_indent + indentString * level

	def dedent( self, level = 1, indentString = " " ):
		self.initial_indent = self.subsequent_indent = self.initial_indent[:-len( indentString ) * level]

	def wrapMultiLine( self, text, drop_empty_lines = True ):
		out = []
		for line in text.splitlines():
			if not drop_empty_lines and len( line ) == 0:
				out += self.wrap( " " ) # newline
			out += self.wrap( line )

		return out

class XmlReportConverter( MObject ):
	"""Converts a XmlReport instance to HTML, plain text and maybe others

	This is done in multiple ways at the moment
	\li XML: No actions required
	\li Plain text: Deserialize the XML content, generate text output using the lxml classes
	\li others: Use XSL stylesheets to convert XML to the desired format.
	"""

	_XSL_STYLESHEETS = {
		ReportFormat.HTML : "xmlreport2html.xsl",
	}

	def __init__( self, xmlReport ):
		MObject.__init__( self )

		self.__xml = etree.fromstring( xmlReport.getReport() )

		self.__xslTemplateSnippets = {}
		self.__xmlTemplateFunctions = {}
		self.__registeredPlugins = []

		self._initializeXslTemplates()
		self._fetchTemplates( mApp() )

	def convertTo( self, destinationReportFormat ):
		"""Converts the report to destinationFormat, which is one of the keys in _XSL_STYLESHEETS"""

		if destinationReportFormat == ReportFormat.XML:
			return etree.tostring( self.__xml, xml_declaration = True, encoding = "utf-8" ) # no conversion
		elif destinationReportFormat == ReportFormat.HTML:
			return self.convertToHtml()
		elif destinationReportFormat == ReportFormat.TEXT:
			return self.convertToText()

	def _initializeXslTemplates( self ):
		"""Load stylesheets from _XSL_STYLESHEETS into memory"""

		for key, value in self._XSL_STYLESHEETS.items():
			try:
				f = open( os.path.dirname( __file__ ) + '/xslt/{0}'.format( value ) )
				self.__xslTemplateSnippets[key] = etree.XML( f.read() )
			except KeyError:
				raise MomError( "XSL Stylesheet missing: {0}".format( value ) )
			except etree.XMLSyntaxError, e:
				raise MomError( "XSL Stylesheet for {0} is malformed: {1}".format( ReportFormat.toString( key ), e ) )

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
		for destinationReportFormat, markup in plugin.getXslTemplates().items():
			if not destinationReportFormat in self.__xslTemplateSnippets.keys():
				continue # invalid key, no stylesheet registered for that type of XSL

			# search for place to register new plugin templates
			stylesheet = self.__xslTemplateSnippets[destinationReportFormat]
			pluginTemplate = stylesheet.find( ".//{http://www.w3.org/1999/XSL/Transform}template[@match='plugin']" )
			placeholder = pluginTemplate.find( ".//{http://www.w3.org/1999/XSL/Transform}choose" )

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

		functionPointer = plugin.getXmlTemplate
		self.__xmlTemplateFunctions[plugin.getName()] = functionPointer

	def getXslTemplate( self, destinationReportFormat ):
		"""Get the current (modified) XSL stylesheet for the requested format

		\return A etree.Element object or None

		\note May return None if format has no XSL stylesheet associated"""

		# text and XML report format do not have a XSL stylesheet, return None
		if not destinationReportFormat in self.__xslTemplateSnippets:
			return None

		return self.__xslTemplateSnippets[destinationReportFormat]

	def convertToHtml( self ):
		"""Converts the report to HTML using the XSL stylesheet for HTML"""

		transform = etree.XSLT( self.__xslTemplateSnippets[ ReportFormat.HTML ] )
		return str( transform( self.__xml ) )

	def convertToText( self, short = False ):
		"""Converts the report to plain text using the recursive _toText() method"""

		wrapper = _MyTextWrapper( width = 80 )

		if short:
			ignoredTags = ["traceback"]
		else:
			ignoredTags = []

		return "\n".join( self._toText( self.__xml, wrapper, ignoredTags ) )

	def convertToTextSummary( self ):
		wrapper = _MyTextWrapper( replace_whitespace = False, drop_whitespace = False, width = 80 )

		element = self.__xml

		# calculate round trip time from commit to report
		startTime = float_from_node_attribute( element, "plugin", "commitTime" )
		if startTime > 0:
			roundTripTime = formatted_time_delta( datetime.utcnow() - datetime.utcfromtimestamp( startTime ) )
		else:
			roundTripTime = "N/A"

		out = []
		out += wrapper.wrap( "*" * wrapper.width )
		out += wrapper.wrap( "Summary of the {0} Build Report".format( self.__xml.attrib["name"] ) )
		out += " "
		wrapper.indent()
		out += wrapper.wrap( "Build status:   {0}".format( returncode_to_description( int( element.attrib["returncode"] ) ) ) )
		out += wrapper.wrap( "Build time:     {0}".format( string_from_node_attribute( element, "project", "timing" ) ) )
		out += wrapper.wrap( "Report delay:   {0} after commit".format( roundTripTime ) )
		out += " "
		out += wrapper.wrap( "Revision:       {0}".format( string_from_node_attribute( element, "plugin", "revision" ) ) )
		out += wrapper.wrap( "Committer:      {0}".format( string_from_node_attribute( element, "plugin", "committerName" ) ) )
		out += wrapper.wrap( "Time:           {0}".format( string_from_node_attribute( element, "plugin", "commitTimeReadable" ) ) )

		out += " "
		out += wrapper.wrap( "--- Commit message following ---" )
		out += " "
		wrapper.indent( indentString = " " )
		out += wrapper.wrapMultiLine( string_from_node( element, "commitMessage" ), drop_empty_lines = False )
		wrapper.dedent( indentString = " " )
		out += " "
		out += wrapper.wrap( "--- End of commit message ---" )
		out += " "

		wrapper.dedent()
		out += wrapper.wrap( "*" * wrapper.width )
		out += " "

		return "\n".join( out )

	def convertToFailedStepsLog( self ):
		# no wrapper needed

		out = []
		element = self.__xml

		failedSteps = element.findall( './/step[@failed="True"]' )
		for step in failedSteps:
			out += ["*** Step failed: {0} ***".format( step.attrib["name"] )]

			failedActions = step.findall( 'action' )
			for action in failedActions:
				if action.attrib["returncode"] == "0":
					continue # do not show successful actions

				out += ["* Action: {0} *".format( action.find( "logdescription" ).text )]
				out += ["STDOUT:"]
				out += [action.find( "stdout" ).text]
				out += ["STDERR:"]
				out += [action.find( "stderr" ).text]
				out += " "
			out += " "

		return "\n".join( out )

	def _toText( self, element, wrapper, ignoredTags ):
		"""Recursive method for parsing an ElementTree and converting it to plain text"""

		out = []

		if element.tag in ignoredTags:
			return out

		# exception stuff
		if element.tag == "exception":
			out += " "
			out += wrapper.wrap( "Exception: {1} (returned {0})".format( element.attrib["returncode"], element.attrib["type"] ) )
		elif element.tag == "description":
			out += wrapper.wrapMultiLine( "Description: {0}".format( element.text ) )
		elif element.tag == "traceback":
			out += wrapper.wrapMultiLine( element.text )

		elif element.tag == "build":
			out += wrapper.wrap( "Build: {0}".format( element.attrib["name"] ) )
			out += " "
			wrapper.indent()
			out += wrapper.wrap( "Platform:     {0} ({1})".format( element.attrib["sys-platform"], element.attrib["sys-version"] ) )
			out += wrapper.wrap( "Architecture: {0}".format( element.attrib["sys-architecture"] ) )
			out += wrapper.wrap( "Node name:    {0}".format( element.attrib["sys-nodename"] ) )
			out += " "
			out += wrapper.wrap( "Build status: {0}".format( returncode_to_description( int( element.attrib["returncode"] ) ) ) )
			wrapper.dedent()

		elif element.tag == "project":
			out += " "
			out += wrapper.wrap( "Project: {0}".format( element.attrib["name"] ) )
			out += " "
			wrapper.indent()
			#out += wrapper.wrap( "Base directory: {0}".format( element.attrib["basedir"] ) )
			#out += " "
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
			description = element.find( "plugindescription" ).text

			if description is not None:
				out += wrapper.wrap( "{0}: {1}".format( name, description ) )
			else:
				out += wrapper.wrap( name )

			if name in self.__xmlTemplateFunctions:
				wrapper.indent()
				try:
					text = self.__xmlTemplateFunctions[name]( element, wrapper )
				except Exception:
					mApp().debug( self, "Exception in getXmlTemplate function for plugin {0}".format( name ) )
					text = wrapper.wrap( "(Exception while getting plugin report, see log)" )
				wrapper.dedent()

				if text is not None:
					out += text

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

		wrapper.indent()
		for childElement in element.getchildren():
			out += self._toText( childElement, wrapper, ignoredTags ) # enter recursion
		wrapper.dedent()

		return out
