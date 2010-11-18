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
from core.Exceptions import MomError
from core.MObject import MObject
from core.helpers.FilesystemAccess import make_foldername_from_string
from core.helpers.TypeCheckers import check_for_string
from core.helpers.TimeKeeper import TimeKeeper
from core.helpers.GlobalMApp import mApp

class Step( MObject ):
	"""An individual step of an Executomat run."""
	def __init__( self, stepName = None ):
		MObject.__init__( self, stepName, "step" )
		self.__timeKeeper = TimeKeeper()
		self.__enabled = True
		self.__ignorePreviousFailure = False
		self.__preActions = [] # list of preparation actions
		self.__mainActions = [] # list of main actions
		self.__postActions = [] # list of post actions
		self.__logfileName = None
		self.__failed = False
		self.__skipped = False

	def failed( self ):
		return self.__failed

	def setEnabled( self, enabled = True ):
		self.__enabled = enabled

	def isEnabled( self ):
		return self.__enabled

	def wasSkipped( self ):
		return self.__skipped

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

	def addMainAction( self, action ):
		"""Add a main command."""
		self.__addAction( self.getMainActions(), action )

	def addPostAction( self, action ):
		"""Add a post command"""
		self.__addAction( self.getPostActions(), action )

	def getTimeKeeper( self ):
		return self.__timeKeeper

	def __addAction( self, container, action ):
		container.append( action )

	def _logEnvironment( self, executomat ):
		mApp().debugN( self, 5, 'environment before executing step "{0}":'.format( self.getName() ) )
		for key in os.environ:
			mApp().debugN( self, 5, '--> {0}: {1}'.format( key, os.environ[key] ) )

	def execute( self, instructions ):
		"""Execute the step"""
		try:
			with self.getTimeKeeper():
				if not self.getName():
					raise MomError( "Cannot execute a step with no name!" )
				if not self.__enabled:
					mApp().debugN( self, 2, 'step "{0}" disabled, skipping.'.format( self.getName() ) )
					return True
				if instructions.hasFailed() and not self.getExecuteOnFailure():
					mApp().debugN( self, 4, 'aborting because of errors earlier in the build' )
					return True
				self._logEnvironment( instructions )

				logfileName = '{0}.log'.format( make_foldername_from_string( self.getName() ) )
				logfileName = os.path.join( instructions._getLogDir(), logfileName )
				self.setLogfileName( logfileName )

				phases = [ [ 'preparatory actions', self.__preActions ],
						[ 'main actions', self.__mainActions ],
						[ 'post actions', self.__postActions ] ]
				for phase, actions in phases:
					if not actions:
						mApp().debugN( self, 3, 'phase "{0}" is empty (no actions registered)'.format( phase ) )
					for action in actions:
						if not self.__failed or action.getIgnorePreviousFailure():
							result = action.executeAction( self, instructions )
							resultText = 'successful'
							if result != 0:
								resultText = 'failed'
							mApp().debugN( self, 3, '{0}: "{1}" {2}'.format( phase, action.getLogDescription(), resultText ) )
							if result != 0:
								self.__failed = True
						else:
							resultText = 'skipped'
							self.__skipped = True
				return not self.__failed
		finally:
			mApp().debugN( self, 3, 'duration: {0}'.format( self.__timeKeeper.deltaString() ) )

	def describe( self, prefix ):
		MObject.describe( self, prefix )
		if self.getPreActions():
			print( '{0} - pre actions: '.format( prefix ) )
			for action in self.getPreActions():
				action.describe( prefix + '    ' )
		if self.getMainActions():
			print( '{0} - main actions: '.format( prefix ) )
			for action in self.getMainActions():
				action.describe( prefix + '    ' )
		if self.getPostActions():
			print( '{0} - post actions: '.format( prefix ) )
			for action in self.getPostActions():
				action.describe( prefix + '    ' )

	def createXmlNode( self, document ):
		node = MObject.createXmlNode( self, document )
		node.attributes["isEmpty"] = str ( self.isEmpty() )
		node.attributes["isEnabled"] = str( self.isEnabled() )
		node.attributes["timing"] = str( self.__timeKeeper.deltaString() )
		node.attributes["failed"] = str( self.failed() )
		node.attributes["skipped"] = str( self.wasSkipped() )

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
