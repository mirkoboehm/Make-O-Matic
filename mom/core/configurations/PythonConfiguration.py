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
from mom.core.Configuration import Configuration
from mom.core.helpers.RunCommand import RunCommand
import sys

class PythonConfiguration( Configuration ):
	'''PythonConfiguration is used to "build" and test software written in Python.
	It defines the Python executable used by all Python-specific plugins.'''

	def __init__( self, configName = None, executable = sys.executable, parent = None ):
		Configuration.__init__( self, configName, parent )
		self.setExecutable( executable )

	def setExecutable( self, exe ):
		self.__executable = exe

	def getExecutable( self ):
		return self.__executable

	def preFlightCheck( self ):
		'''Check that the configured Python executable exists and can be called.'''
		RunCommand( [self.getExecutable() ] ).checkVersion()
		super( PythonConfiguration, self ).preFlightCheck()
