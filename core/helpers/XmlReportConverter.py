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

from lxml import etree
from _pyio import StringIO
import os.path

class XmlReportConverter( object ):

	TO_HTML = "xmlreport2html.xsl"

	def __init__( self, xmlString ):
		self.__xml = xmlString

	def _convertTo( self, fileName ):
		f = open( os.path.dirname( __file__ ) + '/xslt/{0}'.format( fileName ) )
		xsltTree = etree.XML( f.read() )
		transform = etree.XSLT( xsltTree )

		strIO = StringIO( self.__xml )
		doc = etree.parse( strIO )

		return str( transform( doc ) )

	def convertToHtml( self ):
		return self._convertTo( self.TO_HTML )
