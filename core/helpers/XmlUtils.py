# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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

from core.Exceptions import MomException, returncode_to_description
from core.helpers.StringUtils import to_unicode_or_bust

# *** Note ***
# This module should only use stuff from Python's xml.* package, do not depend on external packages for now 

def create_child_node( document, parentNode, tagName, text ):
	elementNode = document.createElement( tagName )
	textNode = document.createTextNode( text )
	elementNode.appendChild( textNode )
	parentNode.appendChild( elementNode )
	return elementNode

def create_exception_xml_node( document, exception, traceback ):
	node = document.createElement( "exception" )

	create_child_node( document, node, "description", to_unicode_or_bust( exception ) )
	create_child_node( document, node, "traceback", to_unicode_or_bust( traceback ) )

	if isinstance( exception, MomException ):
		node.attributes["type"] = returncode_to_description( exception.getReturnCode() )
		node.attributes["returncode"] = unicode( exception.getReturnCode() )
	else:
		node.attributes["type"] = "An unhandled exception occurred"
		node.attributes["returncode"] = unicode( None )

	return node

def string_from_node_attribute( element, node, attribute ):
	for el in element.getiterator( node ):
		if attribute in el.attrib:
			return unicode( el.attrib[attribute] )
	return "N/A"

#	# lxml compatible code
#	try:
#		return element.find( ".//{0}[@{1}]".format( node, attribute ) ).attrib[attribute]
#	except AttributeError:
#		return "N/A"

def float_from_node_attribute( element, node, attribute ):
	for el in element.getiterator( node ):
		if attribute in el.attrib:
			try:
				return float( el.attrib[attribute] )
			except ValueError:
				return - 1
	return - 1

#	# lxml compatible code
#	try:
#		return float( element.find( ".//{0}[@{1}]".format( node, attribute ) ).attrib[attribute] )
#	except AttributeError, ValueError:
#		return - 1

def find_nodes_with_attribute_and_value( element, node, attribute, value ):
	nodes = []
	for el in element.getiterator( node ):
		if attribute in el.attrib:
			if el.attrib[attribute] == value:
				nodes.append( el )
	return nodes

def string_from_node( element, node ):
	try:
		return element.find( ".//{0}".format( node ) ).text
	except AttributeError:
		return "N/A"

def xml_compare( element1, element2, reporter = False ):
	"""From formencode package

	Author: Ian Bicking
	License: MIT License

	Source: http://bitbucket.org/ianb/formencode/src/tip/formencode/doctest_xml_compare.py
	"""

	if element1.tag != element2.tag:
		if reporter:
			print( 'Tags do not match: %s and %s' % ( element1.tag, element2.tag ) )
		return False
	for name, value in element1.attrib.items():
		if element2.attrib.get( name ) != value:
			if reporter:
				print( 'Attributes do not match: %s=%r, %s=%r'
						 % ( name, value, name, element2.attrib.get( name ) ) )
			return False
	for name in element2.attrib.keys():
		if name not in element1.attrib:
			if reporter:
				print( 'element2 has an attribute element1 is missing: %s'
						 % name )
			return False
	if not element1.text == element2.text :
		if reporter:
			reporter( 'text: %r != %r' % ( element1.text, element2.text ) )
		return False
	if not element1.tail == element2.tail:
		if reporter:
			reporter( 'tail: %r != %r' % ( element1.tail, element2.tail ) )
		return False
	cl1 = element1.getchildren()
	cl2 = element2.getchildren()
	if len( cl1 ) != len( cl2 ):
		if reporter:
			reporter( 'children length differs, %i != %i'
					 % ( len( cl1 ), len( cl2 ) ) )
		return False
	i = 0
	for c1, c2 in zip( cl1, cl2 ):
		i += 1
		if not xml_compare( c1, c2, reporter = reporter ):
			if reporter:
				reporter( 'children %i do not match: %s'
						 % ( i, c1.tag ) )
			return False
	return True
