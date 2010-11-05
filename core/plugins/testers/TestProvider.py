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
from core.helpers.TypeCheckers import check_for_path_or_none
from core.actions.ShellCommandAction import ShellCommandAction
from core.helpers.XmlUtils import create_child_node

class TestProvider( Plugin ):

	def __init__( self, name = None ):
		Plugin.__init__( self, name )
		self.__testArgument = None
		self.__action = None

	def _setTestArgument( self, testArgument ):
		check_for_path_or_none( testArgument, "The test argument needs to be a non-empty string" )
		self.__testArgument = testArgument

	def _getTestArgument( self ):
		return self.__testArgument

	def getAction( self ):
		return self.__action

	def getReport( self ):
		return None

	def makeTestStep( self ):
		"""Run tests for the project."""
		cmd = [ self.getCommand() ]
		if self._getTestArgument():
			cmd.append( str( self._getTestArgument() ) )
		step = self.getInstructions().getStep( 'conf-make-test' )
		makeTest = ShellCommandAction( cmd )
		makeTest.setWorkingDirectory( self.getInstructions().getBuildDir() )
		step.addMainAction( makeTest )
		self.__action = makeTest # save

	def setup( self ):
		"""Setup is called after the test steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makeTestStep()

	def getXmlTemplate( self, element, wrapper ):
		return wrapper.wrap( "Report: {0}".format( element.find( "report" ).text ) )

	def createXmlNode( self, document ):
		node = Plugin.createXmlNode( self, document )
		create_child_node( document, node, "report", self.getReport() )
		return node
