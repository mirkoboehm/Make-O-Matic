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

from core.plugins.testers.Analyzer import Analyzer
from core.actions.ShellCommandAction import ShellCommandAction

class TestProviderAction( ShellCommandAction ):
	def __init__( self, tester, command = None, timeout = None ):
		ShellCommandAction.__init__( self, command, timeout )
		self.__tester = tester

	def run( self ):
		try:
			return ShellCommandAction.run( self )
		finally:
			self.__tester.saveReport()

class TestProvider( Analyzer ):

	# Tests should have 100% success rate => minimum = 1.0
	def __init__( self, name = None, minimumScore = 1.0 ):
		Analyzer.__init__( self, name, minimumScore )
		self.__testArgument = None
		self.__action = None

	def getAction( self ):
		return self.__action

	def saveReport( self ):
		raise NotImplementedError

	def createAction( self, cmd ):
		'''Factory method to generate the action that executes the test tool, and processes it's output. 
		To implement custom behavior of the action for a specific test tool, implement an action class that 
		inherits TestProviderAction, and implement a specific run method. Then, overload this method to return an action 
		of the customized type.
		@see TestProviderAction
		'''
		return TestProviderAction( self, cmd )

	def makeTestStep( self ):
		"""Run tests for the project."""
		step = self.getInstructions().getStep( 'conf-make-test' )
		makeTest = self.createAction( self.getCommandWithArguments() )
		makeTest.setWorkingDirectory( self.getInstructions().getBuildDir() )
		step.addMainAction( makeTest )
		self.__action = makeTest # save

	def setup( self ):
		"""Setup is called after the test steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makeTestStep()
