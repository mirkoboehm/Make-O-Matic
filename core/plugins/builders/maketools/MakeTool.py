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
from core.helpers.TypeCheckers import check_for_positive_int, check_for_nonempty_string, \
	check_for_list_of_strings, check_for_int
from core.helpers.RunCommand import RunCommand

class MakeTool():
	'''MakeTool implements an abstract base class for a makefile-parsing build command.'''

	def __init__( self ):
		self.__command = None
		self.__commandSearchPaths = None
		self.__versionParameter = "--version"
		self.__versionOutputLine = 0
		self.__versionReturnCode = 0
		self.__jobs = 1

	def checkVersion( self ):
		RunCommand( [ self.getCommand() ], searchPaths = self.getCommandSearchPaths() ).checkVersion(
			self.getVersionParameter(),
			self.getVersionOutputLine(),
			self.getVersionReturnCode()
		)

	def resolveCommand( self ):
		RunCommand( [ self.getCommand() ], searchPaths = self.getCommandSearchPaths() ).resolveCommand()

	def _setCommand( self, command ):
		check_for_nonempty_string( command, 'The make tool command must be a non-empty string' )
		self.__command = command

	def _setCommandSearchPaths( self, searchPaths ):
		if searchPaths == None:
			searchPaths = []
		check_for_list_of_strings( searchPaths, 'The make tool command search paths must be a list of strings' )
		self.__commandSearchPaths = searchPaths

	def getCommand( self ):
		return self.__command

	def getCommandSearchPaths( self ):
		return self.__commandSearchPaths

	def _setVersionParameter( self, versionParameter ):
		check_for_nonempty_string( versionParameter, 'The make tool version parameter must be a non-empty string.' )
		self.__versionParameter = versionParameter

	def getVersionParameter( self ):
		return self.__versionParameter

	def _setVersionOutputLine( self, versionOutputLine ):
		check_for_positive_int( versionOutputLine, 'The make tool version output line must be a positive integer.' )
		self.__versionOutputLine = versionOutputLine

	def getVersionOutputLine( self ):
		return self.__versionOutputLine

	def _setVersionReturnCode( self, versionReturnCode ):
		check_for_int( versionReturnCode, 'The make tool version expected return code must be an integer.' )
		self.__versionReturnCode = versionReturnCode

	def getVersionReturnCode( self ):
		return self.__versionReturnCode

	def setJobs( self, jobs ):
		check_for_positive_int( jobs, 'The make tool number of jobs must be a positive integer.' )
		self.__jobs = jobs

	def _getJobs( self ):
		return self.__jobs

	def getArguments( self ):
		raise NotImplementedError()
