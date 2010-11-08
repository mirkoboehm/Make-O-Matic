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
import re
from core.actions.CallbackAction import CallbackAction
from core.helpers.GlobalMApp import mApp

class PyUnitTester( TestProvider ):

	def __init__( self, testprogram = None, name = None ):
		TestProvider.__init__( self, name )

		self.setTestProgram( testprogram )

	def setTestProgram( self, program ):
		check_for_path( program, 'The test program must be a Python executable!' )
		self.__program = program

	def getTestProgram( self ):
		return self.__program

	def saveReport( self ):
		mApp().debug( self, "Saving unit test report" )

		stdout = self.getAction().getStdOut()
		if not stdout:
			return

		description = None
		top = 0
		score = 0

		# get total number of tests
		rx = re.compile( 'Ran (\d+) test(s|) in.*', re.MULTILINE | re.DOTALL )
		matches = rx.search( stdout )
		if matches:
			top = int( matches.groups()[0] )

		# get description and number of failed tests
		rx = re.compile( 'FAILED \(failures=(\d+)\)', re.MULTILINE | re.DOTALL )
		matches = rx.search( stdout )
		if matches:
			description = "Make test FAILED."
			score = top - int( matches.groups()[0] )
		else:
			description = "Make test succeeded."
			score = top

		self._setDescription( description )
		self._setScore( score, top )

	def performPreFlightCheck( self ):
		# check if instructions object is of correct type
		pyConf = self.getInstructions()
		if not isinstance( pyConf, PythonConfiguration ):
			raise MomError( 'A PyUnitTester can only be assigned to a PythonConfiguration!' )
		if not self.getTestProgram():
			raise ConfigurationError( 'A Python test program needs to be specified (setTestProgram)!' )

		# set runners
		self._setCommand( pyConf.getExecutable() )
		self._setTestArgument( self.getTestProgram() )

	def setup( self ):
		TestProvider.setup( self )

		# set savereport callback
		action = CallbackAction( self, PyUnitTester.saveReport )
		step = self.getInstructions().getStep( 'conf-make-test' )
		step.addPostAction( action )
