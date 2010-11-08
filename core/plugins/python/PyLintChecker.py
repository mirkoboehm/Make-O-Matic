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
from core.helpers.GlobalMApp import mApp

class _PyLintCheckerAction( Action ):
	'''_PyLintCheckerAction executes PyLint and parses it's output'''

	def __init__( self, pyLintChecker ):
		Action.__init__( self )
		self.__pyLintChecker = pyLintChecker

	def getLogDescription( self ):
		return '{0}'.format( self.getName() )

	def _getPyLintChecker( self ):
		return self.__pyLintChecker

	def run( self ):
		"""Executes the shell command. Needs a command to be set."""
		cmd = [ self._getPyLintChecker().getCommand() ]

		args = [ ]
		if self._getPyLintChecker().getPyLintRcFile():
			args.append( '--rcfile={0}'.format( self._getPyLintChecker().getPyLintRcFile() ) )

		# First, run PyLint with parseable output, and retrieve the score and comment:
		parseableCommand = cmd + [ '--output-format=parseable' ] + args + self._getPyLintChecker().getModules()
		runner1 = RunCommand( parseableCommand, 1800 )
		runner1.run()
		if runner1.getReturnCode() >= 32:
			mApp().debugN( self, 2, 'error running pylint to produce the parseable report' )
			return 1

		# parse output
		self._getPyLintChecker().parsePyLintOutput( runner1.getStdOut() )

		# Second step, run pylint again, to produce the full HTML report:
		if self._getPyLintChecker().getHtmlOutputPath():
			htmlCommand = cmd + [ '--output-format=html' ] + args + self._getPyLintChecker().getModules()
			runner2 = RunCommand( htmlCommand )
			runner2.run()
			if runner2.getReturnCode() >= 32:
				mApp().debugN( self, 2, 'error running pylint to generate the HTML report' )
				return 1
			path = str( self._getPyLintChecker().getHtmlOutputPath() )
			try:
				with open( path, 'w' ) as file:
					file.write( runner2.getStdOut() )
				mApp().debugN( self, 2, 'pylint html report is at "{0}"'.format( path ) )
			except IOError as e:
				mApp().debug( self, 'ERROR saving pylint html report to "{0}": {1}'.format( path, e ) )
				return 1
		return 0

class PyLintChecker( Analyzer ):

	def __init__( self, pyLintTool = None, pyLintRcFile = None, htmlOutputPath = None, modules = None, name = None ):
		Analyzer.__init__( self, name )
		self._setCommand( pyLintTool )
		self.setModules( modules )
		self.setPyLintRcFile( pyLintRcFile )
		self._setScore( 0.0, 0.0 )
		self._setDescription( None )
		self.setHtmlOutputPath( htmlOutputPath )

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

	def parsePyLintOutput( self, output ):
		rx = re.compile( 'rated at (.+?)/([\d.]+)(.*)', re.MULTILINE | re.DOTALL )
		matches = rx.search( output )
		if matches and len( matches.groups() ) == 3:
			score = float( matches.groups()[0] )
			top = float( matches.groups()[1] )
			description = re.sub( '\s+', ' ', matches.groups()[2].strip() )

			self._setScore( score, top )
			self._setDescription( description )
			mApp().debugN( self, 2, 'pylint score is {0}/{1}: {2}.'.format( score, top, description ) )

	def setHtmlOutputPath( self, path ):
		check_for_path_or_none( path, 'The HTML output path must be a file system path!' )
		self.__htmlPath = path

	def getHtmlOutputPath( self ):
		return self.__htmlPath

	def performPreFlightCheck( self ):
		pyConf = self.getInstructions()
		if not isinstance( pyConf, PythonConfiguration ):
			raise MomError( 'A PyUnitTester can only be assigned to a PythonConfiguration!' )
		return Analyzer.performPreFlightCheck( self )

	def setup( self ):
		action = _PyLintCheckerAction( self )
		action.setWorkingDirectory( self.getInstructions().getProject().getSourceDir() )
		step = self.getInstructions().getStep( 'conf-make-test' )
		step.addMainAction( action )
		return Analyzer.setup( self )
