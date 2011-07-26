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

from mom.core.Exceptions import MomError, ConfigurationError
from mom.core.MObject import MObject
from mom.core.Settings import Settings
from mom.core.actions.Action import Action
from mom.core.helpers.Enum import Enum
from mom.core.helpers.FilesystemAccess import make_foldername_from_string
from mom.core.helpers.GlobalMApp import mApp
from mom.core.helpers.StringUtils import make_posixpath
from mom.core.helpers.TimeKeeper import TimeKeeper
from mom.core.helpers.TypeCheckers import check_for_string, check_for_nonempty_string
import os

class Step( MObject ):

	class Result( Enum ):
		'''Enumerated values representing the result of a step.'''
		NotExecuted, Success, Failure = range ( 3 )
		_Descriptions = [ 'not executed', 'success', 'failure' ]

	class Status( Enum ):
		'''Enumerated values representing the status of a step.'''
		New, Skipped_Disabled, Started, Finished, Skipped_PreviousError = range( 5 )
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
		self.__logfilePath = None

	def setStatus( self, status ):
		if status in ( Step.Status.New, Step.Status.Skipped_Disabled, Step.Status.Started,
					Step.Status.Finished, Step.Status.Skipped_PreviousError ):
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
		for actions in self.getAllActions():
			if len( actions ) > 0:
				return False

		return True

	def setLogfilePath( self, logfileName ):
		check_for_string( logfileName, "The log file parameter must be a string containing a file name." )
		self.__logfilePath = logfileName

	def getLogfilePath( self ):
		return self.__logfilePath

	def _getRelativeLogFilePath( self ):
		"""\return Relative path of log file to the build base directory"""

		if not self.getLogfilePath():
			return None

		appBaseDir = mApp().getBaseDir()
		return os.path.relpath( self.getLogfilePath(), appBaseDir )

	def getRelativeLinkTarget( self ):
		unixPath = make_posixpath( self._getRelativeLogFilePath() )

		return ( unixPath, "Get log file for this step" )

	def getPreActions( self ):
		return self.__preActions

	def getMainActions( self ):
		return self.__mainActions

	def getPostActions( self ):
		return self.__postActions

	def getAllActions( self ):
		"""\return 3-Element-List of List of actions ([[..],[..],[..]])"""

		return [self.getPreActions(), self.getMainActions(), self.getPostActions()]

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

	def _getPhases( self ):
		"""\return List of three (str, [Action]) tuples

		Contains description and list of actions for each phase (pre, main, post)"""

		return [
			( 'preparatory actions', self.__preActions ),
			( 'main actions', self.__mainActions ),
			( 'post actions', self.__postActions )
		]

	def __addAction( self, container, action, prepend = False ):
		if not isinstance( action, Action ):
			raise ConfigurationError( 'An action needs to implement the Action class (got {0} instead)!'
				.format( repr( action ) if action else 'None' ) )

		if prepend:
			container.insert( 0, action )
		else:
			container.append( action )

	def _logEnvironment( self, executomat ):
		if not mApp().getSettings().get( Settings.ScriptEnableLogEnvironment ):
			return

		mApp().debugN( self, 5, 'environment before executing step "{0}":'.format( self.getName() ) )
		for key in os.environ:
			mApp().debugN( self, 5, '--> {0}: {1}'.format( key, os.environ[key] ) )

	def execute( self, instructions ):
		"""Execute the step"""
		check_for_nonempty_string( self.getName(), "Cannot execute a step with no name!" )
		self.setStatus( Step.Status.Started )
		if not self.isEnabled():
			self.setStatus( Step.Status.Skipped_Disabled )
			return True

		# (usually) abort if another step has failed for this Instructions object:
		if not instructions._stepsShouldExecute() and not self.getExecuteOnFailure():
			self.setStatus( Step.Status.Skipped_PreviousError )
			return True

		with self.getTimeKeeper():
			self._logEnvironment( instructions )

			logfileName = '{0}.log'.format( make_foldername_from_string( self.getName() ) )
			logfilePath = os.path.join( instructions.getLogDir(), logfileName )
			self.setLogfilePath( logfilePath )
			self.setResult( Step.Result.Success )

			# execute each action associated to this step
			for phase, actions in self._getPhases():
				if not actions:
					mApp().debugN( self, 3, 'phase "{0}" is empty (no actions registered)'.format( phase ) )
					continue

				mApp().debugN( self, 3, 'phase "{0}" has {1} actions registered, starting execution'.format( phase, len( actions ) ) )
				for action in actions:
					resultText = 'skipped'
					if self.getResult() != Step.Result.Failure or action.getIgnorePreviousFailure():
						result = action.executeAction( self.getLogfilePath() )
						resultText = 'successful' if result == 0 else 'failed'
						if result != 0:
							self.setResult( Step.Result.Failure )
					else:
						self.setStatus( Step.Status.Skipped_PreviousError )
					mApp().debugN( self, 3, '{0}: "{1}" {2}'.format( phase, action.getLogDescription(), resultText ) )
			self.setStatus( Step.Status.Finished )
			return self.getResult() != Step.Result.Failure

	def describe( self, prefix, details = None, replacePatterns = True ):
		if self.isEmpty():
			return

		super( Step, self ).describe( prefix, details, replacePatterns )
		for phase in self._getPhases():
			for action in phase[1]:
				action.describe( prefix, details = phase[0] )

	def createXmlNode( self, document ):
		node = super( Step, self ).createXmlNode( document )
		node.attributes["isEmpty"] = str ( self.isEmpty() )
		node.attributes["isEnabled"] = str( self.isEnabled() )
		node.attributes["timing"] = str( self.__timeKeeper.deltaString() )
		node.attributes["result"] = str( self.Result.getKey( self.getResult() ) )
		node.attributes["status"] = str( self.Status.getKey( self.getStatus() ) )

		for actions in self.getAllActions():
			if not actions:
				continue
			for action in actions:
				element = action.createXmlNode( document )
				node.appendChild( element )

		return node
