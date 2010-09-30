# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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

from core.Plugin import Plugin
from core.helpers.TypeCheckers import check_for_nonempty_string
from core.actions.ShellCommandAction import ShellCommandAction

class TestProvider( Plugin ):

	def __init__( self, name = None ):
		"""Constructor"""
		Plugin.__init__( self, name )
		self.__testArgument = None

	def _setTestArgument( self, testArgument ):
		check_for_nonempty_string( testArgument, "The test argument needs to be a non-empty string" )
		self.__testArgument = testArgument

	def _getTestArgument( self ):
		return self.__testArgument

	def makeTestStep( self ):
		"""Run tests for the project."""
		if self._getTestArgument() == None:
			raise NotImplementedError()
		step = self.getInstructions().getStep( 'conf-make-test' )
		makeTest = ShellCommandAction( [ self.getCommand(), self._getTestArgument() ] )
		makeTest.setWorkingDirectory( self.getInstructions().getBuildDir() )
		step.addMainAction( makeTest )

	def setup( self ):
		"""Setup is called after the test steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makeTestStep()
