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

import os
from core.Exceptions import MomError, ConfigurationError
from core.MObject import MObject
from core.helpers.FilesystemAccess import make_foldername_from_string
from core.helpers.TypeCheckers import check_for_string, check_for_nonempty_string
from core.helpers.TimeKeeper import TimeKeeper
from core.helpers.GlobalMApp import mApp
from core.helpers.Enum import Enum

class Step( MObject ):

	class Result( Enum ):
		'''Enumerated values representing the result of a step.'''
		NotExecuted, Success, Failure = range ( 3 )
		_Descriptions = [ 'not executed', 'success', 'failure' ]

	class Status( Enum ):
		'''Enumerated values representing the status of a step.'''
		New, Skipped_Disabled, Started, Finished, Skipped_Error = range( 5 )
		_Descriptions = [ 'new', 'skipped (disabled)', 'started', 'finished', 'skipped (previous error)' ]

	"""An individual step of an Executomat run."""
	def __init__( self, stepName = None ):
		MObject.__init__( self, stepName )
		self.setStatus( Step.Status.New )
		self.setResult( Step.Result.NotExecuted )
		self.__timeKeeper = TimeKeeper()
		self.__enabled = True
		self.__ignorePreviousFailure = False
		self.__preActions = [] # list of preparation actions
		self.__mainActions = [] # list of main actions
		self.__postActions = [] # list of post actions
		self.__logfileName = None

	def setStatus( self, status ):
		if status in ( Step.Status.New, Step.Status.Skipped_Disabled, Step.Status.Started,
					Step.Status.Finished, Step.Status.Skipped_Error ):
			self.__status = status
		else:
			raise MomError( 'Unknown step status {0}'.format( status ) )

	def getStatus( self ):
		return self.__status

	def setResult( self, result ):
		if result in ( Step.Result.NotExecuted, Step.Result.Success, Step.Result.Failure ):
			self.__result = result
		else:
			raise MomError( 'Unknown step result {0}'.format( result ) )

	def getResult( self ):
		return self.__result

	def setEnabled( self, enabled = True ):
		self.__enabled = enabled

	def isEnabled( self ):
		return self.__enabled

	def setIgnorePreviousFailure( self, doIt ):
		"""Set execute-on-failure. If true, the command will be executed, even if a previous command of the same sequence failed."""
		self.__ignorePreviousFailure = doIt

	def getExecuteOnFailure( self ):
		return self.__ignorePreviousFailure

	def isEmpty( self ):
		return not self.getPreActions() and not self.getMainActions() and not self.getPostActions()

	def setLogfileName( self, logfileName ):
		check_for_string( logfileName, "The log file parameter must be a string containing a file name." )
		self.__logfileName = logfileName

	def getLogfileName( self ):
		return self.__logfileName

	def getPreActions( self ):
		return self.__preActions

	def getMainActions( self ):
		return self.__mainActions

	def getPostActions( self ):
		return self.__postActions

	def addPreAction( self, action ):
		"""Add one precommand."""
		self.__addAction( self.getPreActions(), action )

	def prependPreAction( self, action ):
		"""Prepend one precommand."""
		self.__addAction( self.getPreActions(), action, True )

	def addMainAction( self, action ):
		"""Add a main command."""
		self.__addAction( self.getMainActions(), action )

	def prependMainAction( self, action ):
		"""Prepend a main command."""
		self.__addAction( self.getMainActions(), action, True )

	def addPostAction( self, action ):
		"""Add a post command"""
		self.__addAction( self.getPostActions(), action )

	def prependPostAction( self, action ):
		"""Prepend a post command"""
		self.__addAction( self.getPostActions(), action, True )

	def getTimeKeeper( self ):
		return self.__timeKeeper

	def __addAction( self, container, action, prepend = False ):
		from core.actions.Action import Action
		if not isinstance( action, Action ):
			raise ConfigurationError( 'An action needs to implement the Action class (got {0} instead)!'
				.format( repr( action ) if action else 'None' ) )
		if prepend:
			container.insert( 0, action )
		else:
			container.append( action )

	def _logEnvironment( self, executomat ):
		mApp().debugN( self, 5, 'environment before executing step "{0}":'.format( self.getName() ) )
		for key in os.environ:
			mApp().debugN( self, 5, '--> {0}: {1}'.format( key, os.environ[key] ) )

	def execute( self, instructions ):
		"""Execute the step"""
		check_for_nonempty_string( self.getName(), "Cannot execute a step with no name!" )
		if not self.isEmpty():
			mApp().debugN( self, 2, 'starting step "{0}"'.format( self.getName() ) )
		self.setStatus( Step.Status.Started )
		if not self.isEnabled():
			self.setStatus( Step.Status.Skipped_Disabled )
			return True
		# (usually) abort if another step has failed for this Instructions object:
		if not instructions._stepsShouldExecute() and not self.getExecuteOnFailure():
			self.setStatus( Step.Status.Skipped_Error )
			return True
		with self.getTimeKeeper():
			self._logEnvironment( instructions )

			logfileName = '{0}.log'.format( make_foldername_from_string( self.getName() ) )
			logfileName = os.path.join( instructions.getLogDir(), logfileName )
			self.setLogfileName( logfileName )

			phases = [ [ 'preparatory actions', self.__preActions ],
					[ 'main actions', self.__mainActions ],
					[ 'post actions', self.__postActions ] ]
			self.setResult( Step.Result.Success )
			for phase, actions in phases:
				if not actions:
					mApp().debugN( self, 3, 'phase "{0}" is empty (no actions registered)'.format( phase ) )
				for action in actions:
					resultText = 'skipped'
					if self.getResult() != Step.Result.Failure or action.getIgnorePreviousFailure():
						result = action.executeAction( self, instructions )
						resultText = 'successful' if result == 0 else 'failed'
						if result != 0:
							self.setResult( Step.Result.Failure )
					else:
						self.setStatus( Step.Status.Skipped_Error )
					mApp().debugN( self, 3, '{0}: "{1}" {2}'.format( phase, action.getLogDescription(), resultText ) )
			self.setStatus( Step.Status.Finished )
			return self.getResult() != Step.Result.Failure

	def describe( self, prefix, details = None, replacePatterns = True ):
		if not self.isEmpty():
			MObject.describe( self, prefix, details, replacePatterns )
			for phase in [ [ ' pre', self.getPreActions() ],
							[ 'main', self.getMainActions() ],
							[ 'post', self.getPostActions() ] ]:
				for action in phase[1]:
					action.describe( prefix, details = phase[0] )

	def createXmlNode( self, document ):
		node = MObject.createXmlNode( self, document )
		node.attributes["isEmpty"] = str ( self.isEmpty() )
		node.attributes["isEnabled"] = str( self.isEnabled() )
		node.attributes["timing"] = str( self.__timeKeeper.deltaString() )
		node.attributes["result"] = str( self.Result.getKey( self.getResult() ) )
		node.attributes["status"] = str( self.Status.getKey( self.getStatus() ) )

		if self.getPreActions():
			for action in self.getPreActions():
				element = action.createXmlNode( document )
				node.appendChild( element )
		if self.getMainActions():
			for action in self.getMainActions():
				element = action.createXmlNode( document )
				node.appendChild( element )
		if self.getPostActions():
			for action in self.getPostActions():
				element = action.createXmlNode( document )
				node.appendChild( element )

		return node
