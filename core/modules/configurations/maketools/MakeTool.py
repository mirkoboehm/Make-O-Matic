# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, \
	check_for_positive_int
from core.Exceptions import AbstractMethodCalledError

class MakeTool():
	'''MakeTool implements an abstract base class for a makefile-parsing build command.'''

	def __init__( self ):
		self.__command = None
		self.__jobs = 1

	def getVersion( self ):
		raise AbstractMethodCalledError()

	def setCommand( self, command ):
		check_for_nonempty_string_or_none( command, 'The make tool command must be a non-empty string, or None.' )
		self.__command = command

	def getCommand( self ):
		return self.__command

	def setJobs( self, jobs ):
		check_for_positive_int( jobs, 'The make tool number of jobs must be a positive integer.' )
		self.__jobs = jobs

	def _getJobs( self ):
		return self.__jobs

	def getArguments( self ):
		raise AbstractMethodCalledError()
