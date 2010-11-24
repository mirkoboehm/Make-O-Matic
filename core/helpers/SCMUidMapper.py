# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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
import re

class SCMUidMap():

	def getEmail( self, uid ):
		"""Returns the email address for the given UID or None"""

		raise NotImplementedError()

class SCMUidDictMap( SCMUidMap ):

	def __init__( self, dictMap ):
		assert isinstance( dictMap, dict )
		self._dict = dictMap

	def getEmail( self, uid ):
		if uid in self._dict:
			return self._dict[uid]
		else:
			return None

class SCMUidSvnAuthorsFileMap( SCMUidDictMap ):

	def __init__( self, filePath ):
		SCMUidDictMap.__init__( self, {} )

		self.__filePath = filePath
		self.reloadFile()

	def reloadFile( self ):
		f = open( self.__filePath, 'r' )
		content = f.read()

		rx = re.compile( '(\w+) = \w+ <(.+)>', re.MULTILINE )
		matches = rx.findall( content )
		for match in matches:
			self._dict[match[0]] = match[1]

		f.close()

class SCMUidMapper():

	def __init__( self, scm ):
		self.__scm = scm
		self.__maps = []

	def addDict( self, dictMap ):
		"""Convenience method to add a dict right away"""

		self.addMapping( SCMUidDictMap( dictMap ) )

	def addMapping( self, map ):
		"""Add a mapping to the mapper, last added mapping is used first for finding the email address"""

		if not map:
			return

		assert isinstance( map, SCMUidMap )
		self.__maps.append( map )

	def getEmail( self, uid ):
		"""Returns the email address for the given uid or None.
		
		Searches through all the available mappings. Last added mapping is evaluated first."""

		for map in reversed( self.__maps ):
			email = map.getEmail( uid )
			if email:
				return email

		return None

	def getScm( self ):
		return self.__scm
