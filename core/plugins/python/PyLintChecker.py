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
from core.plugins.testers.Analyzer import Analyzer
from core.helpers.TypeCheckers import check_for_list_of_paths_or_none, check_for_path_or_none
from core.plugins.python.PythonConfiguration import PythonConfiguration
from core.Exceptions import MomError
from core.actions.Action import Action
from core.helpers.RunCommand import RunCommand
import re
from test.test_iterlen import len
from core.helpers.GlobalMApp import mApp

class _PyLintCheckerAction( Action ):
	'''_PyLintCheckerAction executes PyLint and parses it's output'''

	def __init__( self, pyLintChecker, args ):
		Action.__init__( self )
		self.__pyLintChecker = pyLintChecker
		self._args = args

	def getLogDescription( self ):
		return '{0}'.format( self.getName() )

	def _getPyLintChecker( self ):
		return self.__pyLintChecker

	def run( self ):
		"""Executes the shell command. Needs a command to be set."""
		args = [ self._getPyLintChecker().getCommand() ] + self._args + self._getPyLintChecker().getModules()
		runner = RunCommand( args, 1800 )
		runner.run()
		if runner.getReturnCode() < 32:
			lines = runner.getStdOut()
			rx = re.compile( 'rated at (.+?)/([\d.]+)(.*)', re.MULTILINE | re.DOTALL )
			matches = rx.search( lines )
			if matches and len( matches.groups() ) == 3:
				score = float( matches.groups()[0] )
				top = float( matches.groups()[1] )
				description = re.sub( '\s+', ' ', matches.groups()[2].strip() )
				self._getPyLintChecker()._setScore( score, top )
				self._getPyLintChecker()._setDescription( description )
				mApp().debugN( self, 2, 'pylint score is {0}/{1}: {2}.'.format( score, top, description ) )
				return 0
		mApp().debugN( self, 2, 'error running pylint' )
		return 1

class PyLintChecker( Analyzer ):
	def __init__( self, pyLintTool = None, pyLintRcFile = None, modules = None, name = None ):
		Analyzer.__init__( self, name )
		self._setCommand( pyLintTool )
		self.setModules( modules )
		self.setPyLintRcFile( pyLintRcFile )
		self._setScore( 0.0, 0.0 )
		self._setDescription( None )

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

	def _setScore( self, score, top ):
		self.__score = [ score, top ]

	def getScore( self ):
		return self.__score[0], self.__score[1]

	def _setDescription( self, txt ):
		self.__description = txt

	def getDescription( self ):
		return self.__description

	def performPreFlightCheck( self ):
		pyConf = self.getInstructions()
		if not isinstance( pyConf, PythonConfiguration ):
			raise MomError( 'A PyUnitTester can only be assigned to a PythonConfiguration!' )

	def setup( self ):
		args = [ '--output-format=parseable' ]
		if self.getPyLintRcFile():
			args.append( '--rcfile={0}'.format( self.getPyLintRcFile() ) )
		action = _PyLintCheckerAction( self, args )
		action.setWorkingDirectory( self.getInstructions().getProject().getSourceDir() )
		step = self.getInstructions().getStep( 'conf-make-test' )
		step.addMainAction( action )
