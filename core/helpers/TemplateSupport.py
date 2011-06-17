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

from core.helpers.FilesystemAccess import make_foldername_from_string
from core.helpers.GlobalMApp import mApp
from string import Template

class _TemplateDict( dict ):

	escape = False

	def __init__( self, *args ):
		dict.__init__( self, *args )

		self.__settings = mApp().getSettings()

	def __getitem__( self, key ):
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

	def substitute( self, escape = False ):
		d = _TemplateDict()
		d.escape = escape
		return Template.substitute( self, d )

	def safe_substitute( self, escape = False ):
		d = _TemplateDict()
		d.escape = escape
		return Template.safe_substitute( self, d )

