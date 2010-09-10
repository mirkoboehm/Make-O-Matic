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

import xml.dom.minidom
from core.Instructions import Instructions

class XmlReport( object ):

	def __init__( self, instructions ):
		assert isinstance( instructions, Instructions )
		self.__instructions = instructions
		self.__summary = None
		self.__doc = xml.dom.minidom.Document()

	def getSummary( self ):
		return self.__summary

	def getReport( self ):
		return self.__doc.toxml()

	def prepare( self ):
		#element = self.__doc.createElement( "root" )
		#self.__doc.appendChild( element )
		self.__instructions.describeXmlRecursively( self.__doc, self.__doc )
