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
import os
from mom.core.Exceptions import MomError

class EnvironmentSaver( object ):
	def __enter__( self ):
		self.__environment = os.environ.copy()
		self.__oldCwd = os.getcwd()

	def __exit__( self, type, value, traceback ):
		os.environ.clear()
		for key in self.__environment:
			os.environ[ key ] = self.__environment[ key ]
		if not os.path.isdir( self.__oldCwd ):
			raise MomError( 'The old working directory got deleted and cannot be restored!' )
		if os.getcwd() != self.__oldCwd:
			os.chdir( self.__oldCwd )
