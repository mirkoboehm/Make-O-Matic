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
from core.plugins.testers.Analyser import Analyser
from core.helpers.TypeCheckers import check_for_list_of_paths_or_none, check_for_path_or_none
from core.plugins.python.PythonConfiguration import PythonConfiguration
from core.Exceptions import MomError
from core.actions.Action import Action
from core.helpers.RunCommand import RunCommand

class _PyLintCheckerAction( Action ):
	'''_PyLintCheckerAction executes PyLint and parses it's output'''

	def __init__( self, pyLintChecker, args ):
		Action.__init__( self )
		self.__pyLintChecker = pyLintChecker
		self.__args = args

	def getLogDescription( self ):
		return '{0}'.format( self.getName() )

	def run( self ):
		"""Executes the shell command. Needs a command to be set."""
		runner = RunCommand( self.__command, 1800 )
		# FIXME set working directory to source directory
		runner.run()
		if runner.getReturnCode() == 0:
			# FIXME parse pylint output
			return 1
		return 1

class PyLintChecker( Analyser ):
	def __init__( self, pyLintTool = None, pyLintRcFile = None, modules = None, name = None ):
		Analyser.__init__( self, name )
		self._setCommand( pyLintTool )
		self.setModules( modules )
		self.setPyLintRcFile( pyLintRcFile )

	def setModules( self, modules ):
		check_for_list_of_paths_or_none( modules, 'The PyLint modules must be a list of paths!' )
		self.__modules = modules

	def getModules( self ):
		return self.__modules

	def setPyLintRcFile( self, file ):
		check_for_path_or_none( file, 'The pylint RC file must be a path!' )
		self.__rcFile = file

	def getPyLintRcFile( self ):
		return self.__rcFile

	def performPreFlightCheck( self ):
		pyConf = self.getInstructions()
		if not isinstance( pyConf, PythonConfiguration ):
			raise MomError( 'A PyUnitTester can only be assigned to a PythonConfiguration!' )

	def setup( self ):
		args = [ '--output-format=parseable', '--reports=no' ]
		if self.getPyLintRcFile():
			args.append( [ '--rcfile={0}'.format( self.getPyLintRcFile() ) ] )
		action = _PyLintCheckerAction( self, args )
		step = self.getInstructions().getStep( 'conf-make-test' )
		step.addMainAction( action )
