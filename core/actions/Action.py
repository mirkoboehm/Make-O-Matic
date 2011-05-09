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

from core.MObject import MObject
from core.helpers.TypeCheckers import check_for_nonnegative_int, check_for_path
from core.Exceptions import MomError, MomException, BuildError
import os, sys
from core.helpers.TimeKeeper import TimeKeeper
from core.helpers.GlobalMApp import mApp
from core.helpers.XmlUtils import create_child_node
from core.helpers.EnvironmentSaver import EnvironmentSaver
import traceback
from core.helpers.StringUtils import to_unicode_or_bust
import codecs

class Action( MObject ):
	"""Action is the base class for executomat actions.
	Every action has a working directory, and an integer result. A result of zero (0) indicates success.
	The output is registered separately for (potentially imaginary) stdout and stderr streams, and can be 
	saved to a log file. 
	"""

	def run( self ):
		'''run() executes the workload of the action. 
		Run must return a non-negative integer number. 
		A return value or zero indicates success. Any value different from zero is considered an error.'''
		raise NotImplementedError()

	def getObjectDescription( self ):
		return self.getLogDescription()

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		raise NotImplementedError()

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.__timeKeeper = TimeKeeper()
		self.__workingDir = None
		self.__started = False
		self.__finished = False
		self.__aborted = False
		self.__result = None
		self._setStdOut( None )
		self._setStdErr( None )
		self.setIgnorePreviousFailure( False )

	def setWorkingDirectory( self, workingDir ):
		"""Set the directory to execute the command in."""
		check_for_path( workingDir, "The working directory parameter must be a string containing a directory name." )
		self.__workingDir = workingDir

	def getWorkingDirectory( self ):
		"""Return the working directory."""
		return self.__workingDir

	def _aboutToStart( self ):
		self.__started = True

	def wasStarted( self ):
		return self.__started != False

	def setIgnorePreviousFailure( self, onOff ):
		'''If true, the action will be executed even if a previous action of the same step failed.'''
		self.__ignorePreviousFailure = onOff

	def getIgnorePreviousFailure( self ):
		return self.__ignorePreviousFailure

	def _finished( self ):
		self.__finished = True

	def didFinish( self ):
		return self.__finished != False

	def _aborted( self ):
		self.__aborted = True

	def getAborted( self ):
		return self.__aborted

	def _setResult( self, result ):
		check_for_nonnegative_int( result, 'The result of an action must be a non-negative integer!' )
		self.__result = result

	def getResult( self ):
		return self.__result

	def _setStdErr( self, err ):
		self.__stdErr = err

	def getStdErr( self ):
		"""Returns the stderr output of the action. Can only be called after execution."""
		if not self.didFinish() and not self.getAborted():
			raise MomError( 'stdErr() queried before the action was finished' )
		return self.__stdErr

	def _setStdOut( self, out ):
		self.__stdOut = out

	def getStdOut( self ):
		"""Returns the stdout output of the action. Can only be called after execution."""
		if not self.didFinish() and not self.getAborted():
			raise MomError( 'stdOut() queried before the action was finished' )
		return self.__stdOut

	def executeAction( self, step, instructions ):
		try:
			with self.__timeKeeper:
				with EnvironmentSaver():
					if self.getWorkingDirectory():
						mApp().debugN( self, 3, 'changing directory to "{0}"'.format( self.getWorkingDirectory() ) )
						try:
							os.chdir( str( self.getWorkingDirectory() ) )
						except ( OSError, IOError ) as e:
							raise BuildError( str( e ) )
					self._aboutToStart()
					mApp().debugN( self, 3, 'executing action {0}'.format( self.getLogDescription() ) )
					try:
						result = self.run()
						if result == None or not isinstance( result, int ):
							raise MomError( 'Action {0} ({1}) did not return a valid non-negative integer return value from run()!'
										.format( self.getName(), self.getLogDescription() ) )
						self._setResult( int( result ) )
						self._finished()
					except MomException as e:
						innerTraceback = "".join( traceback.format_tb( sys.exc_info()[2] ) )
						self._aborted()
						mApp().debug( self, 'execution failed: "{0}"'.format( str( e ) ) )
						mApp().debugN( self, 2, innerTraceback )

						self._setStdErr( "{0}:\n\n{1}".format( e, innerTraceback ) )

						self._setResult( e.getReturnCode() )
					if step.getLogfileName():
						try:
							with codecs.open( step.getLogfileName(), 'a', 'utf-8' ) as f:
								if self.getStdOut() or self.getStdErr():
									f.writelines( 'Output from action "{0}":\n'.format( self.getLogDescription() ) )
									if self.getStdOut():
										f.writelines( '\n=== Standard output ===\n' + self.getStdOut() )
									if self.getStdErr():
										f.writelines( '\n=== Error output ===\n' + self.getStdErr() )
								else:
									f.writelines( '(The action "{0}" did not generate any output.)\n'.format( self.getLogDescription() ) )
						except Exception as e:
							raise MomError( 'cannot write to log file "{0}": {1}'.format( step.getLogfileName(), str( e ) ) )
					return self.getResult()
		finally:
			mApp().debugN( self, 2, '{0} duration: {1}'.format( self.getLogDescription(), self.__timeKeeper.deltaString() ) )

	def getTagName( self ):
		return "action"

	def createXmlNode( self, document ):
		node = MObject.createXmlNode( self, document )

		node.attributes["finished"] = str( self.didFinish() )
		node.attributes["started"] = str( self.wasStarted() )
		node.attributes["timing"] = str( self.__timeKeeper.deltaString() )
		node.attributes["returncode"] = str( self.getResult() )

		stderr, stdout = self._getOutput()
		create_child_node( document, node, "stderr", to_unicode_or_bust( stderr ) )
		create_child_node( document, node, "stdout", to_unicode_or_bust( stdout ) )
		create_child_node( document, node, "logdescription", self.getLogDescription() )

		return node

	def _getOutput( self ):
		try:
			stderr = self.getStdErr()
			stdout = self.getStdOut()
		except MomError:
			stderr = ""
			stdout = ""
		return stderr, stdout

	def describe( self, prefix, details = None, replacePatterns = True ):
		"""Describe this action."""
		self._printDescribeLine( prefix + '    ', details, self.getLogDescription(), replacePatterns )
