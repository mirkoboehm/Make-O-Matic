# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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
import os

class TouchAction( Action ):
	"""TouchAction encapsulates the creation of an empty file or updated the time-stamp on an existing one.
	It is mostly used internally, but can be of general use as well."""
	def __init__( self, file ):
		Action.__init__( self )
		self._file = file

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return 'touch "{0}"'.format( self._file )

	def run( self ):
		"""Touches the list of files."""
		with file( self._file, 'a' ):
			os.utime( self._file, None )
		return 0
