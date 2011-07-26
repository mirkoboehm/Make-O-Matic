# This file is part of Make-O-Matic.
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

from mom.core.helpers.FilesystemAccess import make_foldername_from_string
from mom.core.helpers.GlobalMApp import mApp
from string import Template

class _TemplateDict( dict ):

	escape = False
	overwrites = {}

	def __init__( self, *args ):
		dict.__init__( self, *args )

		self.__settings = mApp().getSettings()

	def __getitem__( self, key ):
		# first: try to get the value from the overwrite dict
		val = self.overwrites.get( key )
		if val != None:
			return val

		# next: try to get it from settings
		val = self.__settings.get( key, True )
		if not val:
			return ""

		if self.escape:
			return make_foldername_from_string( val )

		return val

	def __setitem__( self, key ):
		raise AttributeError( "This dictionary is read-only" )


class MomTemplate( Template ):

	idpattern = r'[_a-z][\._a-z0-9]*'
	overwrites = {}

	def _getDict( self, escape ):
		d = _TemplateDict()
		d.escape = escape

		d.overwrites = self.overwrites
		return d

	def substitute( self, escape = False ):
		d = self._getDict( escape )
		return Template.substitute( self, d )

	def safe_substitute( self, escape = False ):
		d = self._getDict( escape )
		return Template.safe_substitute( self, d )
