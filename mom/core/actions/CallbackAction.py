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

from mom.core.actions.Action import Action
from mom.core.Plugin import Plugin
from mom.core.Exceptions import ConfigurationError

class CallbackAction( Action ):
	"""CallbackAction provides a mechanism to call a method in a specific step

	Just initialize CallbackAction with an object and a method pointer and add the action to some step."""

	def __init__( self, obj, func ):
		if not isinstance( obj, Plugin ):
			raise ConfigurationError( "Can only call methods on Plugin instances" )

		Action.__init__( self )

		self.__obj = obj
		self.__func = func

	def getLogDescription( self ):
		return self.getName()

	def run( self ):
		"""Executes the command."""

		if not self.__obj or not self.__func:
			return 1

		self.__func( self.__obj )
		return 0
