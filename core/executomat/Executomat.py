# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2007 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
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

import os
from core.helpers.TypeCheckers import check_for_string, check_for_nonempty_string
from step import Step
from core.Exceptions import MomError, ConfigurationError
# from AutobuildCore.helpers.exceptdefs import AutoBuildError
# from AutobuildCore.helpers.build_script_helpers import DebugN

class Executomat:
	"""Executomat executes actions in steps which can be individually enabled and disabled.
	The operations are performed as an ordered list of named steps. Each step consists of
	three phases:
	- Preparation: actions that need to be run before the main action
	- Main Action: this is what it is all about (for example, "make")
	- Cleanup: Actions that need to be run after the main command.
	Every step can be enabled or disabled individually. If a step is enabled, all 
	of it's actions need to finish successfully."""

	def __init__( self, name = '' ):
		"""Steps contains series of actions."""
		self.Steps = {}
		self.__name = name
		self.__logfileName = 'execution.log'
		self.__logDir = '.'
		self.__failedStep = None

	def setLogDir( self, path ):
		"""Set the directory where all log information is stored."""
		check_for_string( path, "The log directory name must be a string containing a path name." )
		self.__logDir = path

	def getLogDir( self ):
		"""Return the log dir."""
		return self.__logDir

	def setLogfileName( self, filename ):
		"""Set the file to log activity to."""
		check_for_string( filename, "The log file name must be a string containing a path name." )
		self.__logfileName = filename

	def getlogfileName( self ):
		"""Return the log file name."""
		return self.__logfileName

	def hasFailed( self ):
		return self.__failedStep != None

	def logFilePathForFailedStep( self ):
		if self.__failedStep:
			return self.__failedStep.logFileName()

	def addStep( self, newStep ):
		"""Add a newStep identified by identifier. If the identifier already exists, the new 
		command replaces the old one."""
		if not isinstance( newStep, Step ):
			raise MomError( 'only executomat.Step instances can be added to the queue' )
		check_for_nonempty_string( newStep.name(), "An Executomat step must have a name!" );
		self.Steps[ newStep.getName() ] = newStep

	def addCustomCommands( self, command ):
		assert False # this should be done with the action object
#		"""Add a custom command (either a pre, a post command, or both) to a step.
#		The command is a tuple ( stepid, precmd, type ). Only one command can added 
#		at a time. type is pre or post."""
#		if len( command ) != 3 or not str( command[0] ) or not str( command[1] ) or not str( command[2] ):
#			raise MomError( 'Cannot add custom command. Custom commands are tuples ( stepid, command, type), where type is pre or post.' )
#		step = self.step( command[0] ) # this may raise an AutoBuildError
#		if command[2] == 'pre':
#			# add precommand
#			pass
#		elif command[2] == 'post':
#			# add postcommand
#			pass
#		else:
#			# bad
#			pass
		assert not 'Implemented'

	def getStep( self, identifier ):
		"""Find the step with this identifier and return it."""
		if self.Steps.has_key( identifier ):
			return self.Steps[ identifier ]
		raise MomError( 'no such step "{0}"'.format( identifier ) )

	def log( self, text ):
		"""Write a text to the log file, if it is there."""
		assert False # this is wrong or a misnomer
#		if( self.__logfileName ):
#			self.__logfileName.write( text.rstrip() + '\n' )
#		else:
#			DebugN( 1, text )

	def run( self, project, firstErrorType = -1 ):
		self.__logfileName = None
		try:
			if not os.path.isdir( self.logDir() ):
				raise ConfigurationError( 'Log dir at ' + str( self.logDir() ) + ' does not exist.' )
			if self.__logFileName:
				try:
					self.__logfileName = open( self.logDir() + os.sep + self.__logFileName, 'a' )
				except:
					raise ConfigurationError( 'Cannot open log file at ' + str( self.__logFileName ) )
			self.log( '# Starting execution of ' + self.name() )
			for Step in self.Steps:
				project.debugN( 1, 'now executing step "' + Step[1].name() + '" for "' + self.name() + '"' )
#				if Step[1].execute( self, weHaveIssues ):
#					DebugN( 2, 'success: ' + Step[1].name() )
#				else:
#					self.log( '# aborting execution except for execute-even-on-failure commands\n########' )
#					if firstErrorType == -1:
#						firstErrorType = Step[1].getErrorType()
#					if self.__failedStep == None:
#						# we are only interested in the log files for the first failure 
#						self.__failedStep = Step[1]
#					weHaveIssues = True # sequence failed
#					DebugN( 2, 'failed: ' + Step[1].name() )
			self.log( '# execution finished \n########' )
#			return ( weHaveIssues, firstErrorType )
		finally: # make sure the log file is closed
			if self.__logfileName:
				self.__logfileName.close()

	def report( self ):
		Report = []
		for Step in self.Steps:
			Report.append( Step[1].report() )
		return Report

