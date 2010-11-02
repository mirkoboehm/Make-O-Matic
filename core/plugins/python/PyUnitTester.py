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
from core.plugins.testers.TestProvider import TestProvider
from core.plugins.python.PythonConfiguration import PythonConfiguration
from core.Exceptions import MomError, ConfigurationError
from core.helpers.TypeCheckers import check_for_path

class PyUnitTester( TestProvider ):
	def __init__( self, testprogram = None, name = None ):
		TestProvider.__init__( self, name )
		self.setTestProgram( testprogram )

	def setTestProgram( self, program ):
		check_for_path( program, 'The test program must be a Python executable!' )
		self.__program = program

	def getTestProgram( self ):
		return self.__program

	def performPreFlightCheck( self ):
		pyConf = self.getInstructions()
		if not isinstance( pyConf, PythonConfiguration ):
			raise MomError( 'A PyUnitTester can only be assigned to a PythonConfiguration!' )
		if not self.getTestProgram():
			raise ConfigurationError( 'A Python test program needs to be specified (setTestProgram)!' )
		self._setCommand( pyConf.getExecutable() )
		self._setTestArgument( self.getTestProgram() )


