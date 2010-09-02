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
from core.helpers.TypeCheckers import check_for_nonnegative_int, check_for_path
from core.Exceptions import AbstractMethodCalledError, MomError, MomException, BuildError
import os
from core.helpers.TimeKeeper import TimeKeeper
from core.helpers.GlobalMApp import mApp

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
		raise AbstractMethodCalledError()

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		raise AbstractMethodCalledError()

	def __init__( self, name = None ):
		"""Constructor"""
		MObject.__init__( self, name, "action" )
		self.__timeKeeper = TimeKeeper()
		self.__workingDir = None
		self.__started = False
		self.__finished = False
		self.__aborted = False
		self.__result = None
		self._setStdOut( None )
		self._setStdErr( None )
		self.setIgnorePreviousFailure( False )

	def setWorkingDirectory( self, dir ):
		"""Set the directory to execute the command in."""
		check_for_path( dir, "The working directory parameter must be a string containing a directory name." )
		self.__workingDir = dir

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

	def getExitCode( self ):
		"""Returns the actions integer exit code. Can only be called after execution."""
		if not self.didFinish():
			raise MomError( 'exitCode() queried before the command was finished' )
		return self.__exitCode

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

	def executeAction( self, executomat, step ):
		try:
			self.__timeKeeper.start()
			return self._executeActionTimed( executomat, step )
		finally:
			self.__timeKeeper.stop()
			mApp().debugN( self, 2, '{0} duration: {1}'.format( self.getLogDescription(), self.__timeKeeper.deltaString() ) )

	def _executeActionTimed( self, executomat, step ):
		oldPwd = None
		try:
			if self.getWorkingDirectory():
				oldPwd = os.getcwd()
				executomat.log( '# changing directory to "{0}"'.format( self.getWorkingDirectory() ) )
				try:
					os.chdir( str( self.getWorkingDirectory() ) )
				except ( OSError, IOError ) as e:
					raise BuildError( str( e ) )
			self._aboutToStart()
			executomat.log( '# {0}'.format( self.getLogDescription() ) )
			try:
				result = self.run()
				if result == None or not isinstance( result, int ):
					raise MomError( 'Action {0} ({1}) did not return a valid non-negative integer return value from run()!'
								.format( self.getName(), self.getLogDescription() ) )
				self._setResult( int( result ) )
				self._finished()
			except MomException as e:
				self._aborted()
				mApp().debug( self, 'execution failed: "{0}"'.format( str( e ) ) )
				self._setResult( e.getReturnCode() )
			if step.getLogfileName():
				file = open( step.getLogfileName(), 'a' )
				if file:
					if self.getStdOut():
						file.writelines( self.getStdOut().decode() )
					else:
						file.writelines( '(The action "{0}" did not generate any output.)\n'.format( self.getLogDescription() ) )
					file.close()
				else:
					raise MomError( 'cannot write to log file "{0}"'.format( step.getLogfileName() ) )
			return self.getResult()
		finally:
			if oldPwd:
				executomat.log( '# changing back to "{0}"'.format( oldPwd ) )
				os.chdir( oldPwd )

	def createXmlNode( self, document ):
		node = MObject.createXmlNode( self, document )
		node.attributes["finished"] = str( self.didFinish() )

		stderrElement = document.createElement( "stderr" )
		data = ""
		try:
			data = ( self.getStdErr() if self.getStdErr() != None else "" )
		except:
			pass
		textNode = document.createTextNode( data )
		stderrElement.appendChild( textNode )
		node.appendChild( stderrElement )

		logElement = document.createElement( "logdescription" )
		textNode = document.createTextNode( self.getLogDescription() + data + str( self.getAborted() ) )
		logElement.appendChild( textNode )
		node.appendChild( logElement )

		returncodeElement = document.createElement( "returncode" )
		textNode = document.createTextNode( "{0}".format( self.getResult() ) )
		returncodeElement.appendChild( textNode )
		node.appendChild( returncodeElement )

		return node
