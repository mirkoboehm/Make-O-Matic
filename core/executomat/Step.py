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

import os
from core.Exceptions import MomError
from core.MObject import MObject
from core.helpers.FilesystemAccess import make_foldername_from_string

class Step( MObject ):
	"""An individual step of an Executomat run."""
	def __init__( self, stepName = None ):
		MObject.__init__( self, stepName )
		self.__enabled = True
		self.__preActions = [] # list of preparation actions
		self.__mainActions = [] # list of main actions
		self.__postActions = [] # list of post actions
		self.__logFileName = None
		self.__failed = False

	def failed( self ):
		return self.__failed

	def setEnabled( self, enabled = True ):
		self.__enabled = True

	def getEnabled( self ):
		return self.__enabled

	def logFileName( self ):
		return self.__logFileName

	def getPreActions( self ):
		return self.__preActions

	def getMainActions( self ):
		return self.__mainActions

	def getPostActions( self ):
		return self.__postActions

	def addPreAction( self, action ):
		"""Add one precommand."""
		self.__addAction( self.getPreActions(), action )

	def addMainAction( self, action ):
		"""Add a main command."""
		self.__addAction( self.getMainActions(), action )

	def addPostAction( self, action ):
		"""Add a post command"""
		self.__addAction( self.getPostActions(), action )

	def __addAction( self, container, action ):
		container.append( action )

	def report( self ):
		"""Generate a human readable report about the command execution.
		Every report is a tuple like this: ( 'stepName', 'ok', 'pre: ok, main: ok, post: ok', 'logFileName.log' )"""
		details = ''
		result = [ self.name(), '', '', self.__logFileName ]
		if not self.__enabled:
			result[1] = 'disabled'
			result[2] = result[1]
			return result
		else:
			workSet = ( ['precmds', '', self.__preActions ],
						['maincmds', '', self.__mainActions ],
						['postcmds', '', self.__postActions ] )
			notRun = True
			failed = False
			report = ''
			for phase in workSet:
				if not phase[2]: # no commands for this phase
					phase[1] = 'none'
				else:
					for Cmd in phase[2]:
						if not Cmd.executed():
							phase[1] = 'skipped'
							break
						elif Cmd.timedOut():
							phase[1] = 'timeout (failed)'
							failed = True
							notRun = False
							break
						elif Cmd.exitCode() != 0:
							phase[1] = 'failed'
							failed = True
							notRun = False
							break
						else: # success
							notRun = False
							phase[1] = 'ok'
				if result[2]:
					result[2] += ', '
				result[2] += phase[0] + ': ' + phase[1]
			if notRun:
				result[1] = 'SKIPPED'
			elif failed:
				result[1] += 'FAILED'
			else:
				result[1] += 'success'
			return result

	def execute( self, executomat, project ):
		"""Execute the command"""
		if not self.getName():
			raise MomError( "Cannot execute a command with no name!" )
		if not self.__enabled:
			executomat.log( '# Command ' + self.name() + ' is disabled, skipping.' )
			return True
		executomat.log( '# Executing command "' + self.getName() + '"' )
		executomat.log( '# in ' + os.getcwd() )
		project.debugN( self, 5, 'environment before:' )
		for key in os.environ:
			project.debugN( self, 5, '--> {0}: {1}'.format( key, os.environ[key] ) )
		phases = { 'preparatory actions' : self.__preActions,
				   'main actions' : self.__mainActions,
				   'post actions' : self.__postActions }
		for phase in phases:
			actions = phases[ phase ]
			if actions:
				executomat.log( '# Executing {0}'.format( phase ) )
				for action in actions:
					if action.getWorkingDirectory():
						executomat.log( '# changing directory to "{0}" and back.'.format( action.workingDirectory() ) )
					executomat.log( action.getLogDescription() )
					logfileName = '{0}.log'.format( make_foldername_from_string( self.getName() ) )
					self.__logFileName = executomat.getLogDir() + os.sep + logfileName
					action.setLogfileName( self.__logFileName )
					if action.run( project ) == True:
						executomat.log( '# {0} "{1}" successful (or skipped)'.format( phase, action.getLogDescription() ) )
					else:
						executomat.log( '# {0} "{1}" failed'.format( phase, action.getLogDescription() ) )
						self.__failed = True
						return False # do not continue with the remaining commands
		return True

