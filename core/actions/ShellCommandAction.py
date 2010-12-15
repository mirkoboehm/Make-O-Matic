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

from core.helpers.TypeCheckers import check_for_nonnegative_int, check_for_list_of_strings, check_for_list_of_paths
from core.Exceptions import MomError
from core.helpers.RunCommand import RunCommand
from core.actions.Action import Action

class ShellCommandAction( Action ):
	"""ShellCommandAction encapsulates the execution of one command in the Step class. 
	It is mostly used internally, but can be of general use as well."""

	def __init__( self, command = None, timeout = None, combineOutput = True, searchPaths = None ):
		Action.__init__( self )
		self.setCommand( command, timeout, searchPaths )
		self.__combineOutput = combineOutput
		self.__runner = None

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return '{0}'.format( ' '.join( self.getCommand() ) )

	def setCommand( self, command, timeOutPeriod = None, searchPaths = None ):
		"""Set the shell command"""
		check_for_list_of_paths( command, "The shell command must be a list of strings or paths." )
		if timeOutPeriod != None:
			check_for_nonnegative_int( timeOutPeriod, 'invalid timeout period, valid periods are [0..inf] or None for no timeout' )
		if searchPaths is None:
			searchPaths = []
		check_for_list_of_paths( searchPaths, "The search paths need to be a list of strings." )
		self.__command = command
		self.__timeOutPeriod = timeOutPeriod
		self.__searchPaths = searchPaths

	def getCommand( self ):
		"""Returns the command"""
		return map( lambda x: str( x ) , self.__command )

	def _getRunner( self ):
		if self.__runner == None:
			raise MomError( "The command runner was not initialized before being queried" )
		return self.__runner

	def run( self ):
		"""Executes the shell command. Needs a command to be set."""
		self.__runner = RunCommand( self.__command, self.__timeOutPeriod, self.__combineOutput, self.__searchPaths )
		if self.getWorkingDirectory() != None:
			self.__runner.setWorkingDir( self.getWorkingDirectory() )
		self._getRunner().run()
		self._setStdOut( self._getRunner().getStdOut() )
		self._setStdErr( self._getRunner().getStdErr() )
		return self._getRunner().getReturnCode()

	def hasTimedOut( self ):
		"""Returns True if the shell command process timed out, e.g., was not completed within the timeout period.
		Can only be called after execution."""
		if not self.__started:
			raise MomError( 'timedOut() queried before the command was executed' )
		return self._getRunner().getTimedOut()

