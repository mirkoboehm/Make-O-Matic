# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
# 
# make-o-matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# make-o-matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from core.MObject import MObject
from core.helpers.TypeCheckers import check_for_string
from core.Exceptions import AbstractMethodCalledError, MomError

class Action( MObject ):
	"""Action is the base class for executomat actions.
	Every action has a working directory, and an integer result. A result of zero (0) indicates success.
	The output is registered separately for (potentially imaginary) stdout and stderr streams, and can be 
	saved to a log file. 
	"""

	def run( self, project ):
		raise AbstractMethodCalledError()

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		raise AbstractMethodCalledError()

	def __init__( self, name = "Action" ):
		"""Constructor"""
		MObject.__init__( self, name )
		self.__logfileName = None
		self.__workingDir = None
		self.__started = False
		self.__executeOnFailure = False
		self.__result = 0
		self.__stdOut = ""
		self.__stdErr = ""

	def setLogfileName( self, logfileName ):
		check_for_string( logfileName, "The log file parameter must be a string containing a file name." )
		self.__logfileName = logfileName

	def getLogfileName( self ):
		return self.__logfileName

	def setWorkingDirectory( self, dir ):
		"""Set the directory to execute the command in."""
		check_for_string( dir, "The working directory parameter must be a string containing a directory name." )
		self.__workingDir = dir

	def getWorkingDirectory( self ):
		"""Return the working directory."""
		return self.__workingDir

	def setExecuteOnFailure( self, doIt ):
		"""Set execute-on-failure. If true, the command will be executed, even if a previous command of the same sequence failed."""
		self.__executeOnFailure = doIt

	def getExecuteOnFailure( self ):
		return self.__executeOnFailure

	def wasExecuted( self ):
		return self.__started != False

	def getExitCode( self ):
		"""Returns the actions integer exit code. Can only be called after execution."""
		if not self.wasExecuted():
			raise MomError( 'exitCode() queried before the command was executed' )
		return self.__exitCode

	def getStdErr( self ):
		"""Returns the stderr output of the action. Can only be called after execution."""
		if not self.wasExecuted():
			raise MomError( 'stdErr() queried before the action was executed' )
		return self.__stdErr

	def getStdOut( self ):
		"""Returns the stdout output of the action. Can only be called after execution."""
		if not self.wasExecuted():
			raise MomError( 'stdOut() queried before the action was executed' )
		return self.__stdOut

