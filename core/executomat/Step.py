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
from core.helpers.TypeCheckers import check_for_string
from core.helpers.TimeKeeper import TimeKeeper

class Step( MObject ):
	"""An individual step of an Executomat run."""
	def __init__( self, stepName = None ):
		MObject.__init__( self, stepName )
		self.__timeKeeper = TimeKeeper()
		self.__enabled = True
		self.__executeOnFailure = False
		self.__preActions = [] # list of preparation actions
		self.__mainActions = [] # list of main actions
		self.__postActions = [] # list of post actions
		self.__logfileName = None
		self.__failed = False

	def failed( self ):
		return self.__failed

	def setEnabled( self, enabled = True ):
		self.__enabled = enabled

	def getEnabled( self ):
		return self.__enabled

	def setExecuteOnFailure( self, doIt ):
		"""Set execute-on-failure. If true, the command will be executed, even if a previous command of the same sequence failed."""
		self.__executeOnFailure = doIt

	def getExecuteOnFailure( self ):
		return self.__executeOnFailure

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

	def _logEnvironment( self, project, executomat ):
		project.debugN( self, 5, 'environment before executing step "{0}":'.format( self.getName() ) )
		for key in os.environ:
			project.debugN( self, 5, '--> {0}: {1}'.format( key, os.environ[key] ) )

	def execute( self, executomat, project ):
		try:
			self.__timeKeeper.start()
			return self._executeTimed( executomat, project )
		finally:
			self.__timeKeeper.stop()
			project.debugN( self, 3, 'duration: {0}'.format( self.__timeKeeper.deltaString() ) )

	def _executeTimed( self, executomat, project ):
		"""Execute the step"""
		if not self.getName():
			raise MomError( "Cannot execute a step with no name!" )
		if not self.__enabled:
			executomat.log( 'disabled, skipping.' )
			return True
		if project.getReturnCode() != 0 and not self.getExecuteOnFailure():
			project.debugN( self, 4, 'aborting because of errors earlier in the build' )
			return True
		executomat.log( '# Executing step "{0}"'.format( self.getName() ) )
		executomat.log( '# ... in directory "{0}"'.format( os.getcwd() ) )
		self._logEnvironment( project, executomat )

		logfileName = '{0}.log'.format( make_foldername_from_string( self.getName() ) )
		logfileName = executomat.getLogDir() + os.sep + logfileName
		self.setLogfileName( logfileName )

		phases = { 'preparatory actions' : self.__preActions,
				   'main actions' : self.__mainActions,
				   'post actions' : self.__postActions }
		for phase in phases:
			actions = phases[ phase ]
			if not actions:
				executomat.log( '# Phase "{0}" is empty (no actions registered)'.format( phase ) )
			for action in actions:
				result = action.executeAction( project, executomat, self )
				resultText = 'successful (or skipped)'
				if result != 0:
					resultText = 'failed'
				executomat.log( '# {0} "{1}" {2}'.format( phase, action.getLogDescription(), resultText ) )
				if result != 0:
					self.__failed = True
					return False # do not continue with the remaining actions
		return True

