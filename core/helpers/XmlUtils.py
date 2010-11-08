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

from core.Exceptions import MomException, returncode_to_description

def create_child_node( document, parentNode, tagName, text ):
	elementNode = document.createElement( tagName )
	textNode = document.createTextNode( str( text ) )
	elementNode.appendChild( textNode )
	parentNode.appendChild( elementNode )
	return elementNode

def create_exception_xml_node( document, exception, traceback ):
	node = document.createElement( "exception" )
	create_child_node( document, node, "description", exception )
	create_child_node( document, node, "traceback", traceback )

	if isinstance( exception, MomException ):
		node.attributes["type"] = returncode_to_description( exception.getReturnCode() )
		node.attributes["returncode"] = str( exception.getReturnCode() )
	else:
		node.attributes["type"] = "An unhandled exception occured"
		node.attributes["returncode"] = str( None )

	return node

def string_from_node_attribute( element, node, attribute ):
	try:
		return element.find( ".//{0}[@{1}]".format( node, attribute ) ).attrib[attribute]
	except AttributeError:
		return "N/A"

def string_from_node( element, node ):
	try:
		return element.find( ".//{0}".format( node ) ).text
	except AttributeError:
		return "N/A"
