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
import subprocess, time
from threading import Thread
from core.MObject import MObject
from core.helpers.GlobalMApp import mApp
from core.helpers.TypeCheckers import check_for_positive_int, check_for_path, \
	check_for_list_of_strings
import os.path
import sys
from core.Exceptions import ConfigurationError

class _CommandRunner( Thread ):
	def __init__ ( self , runner ):
		Thread.__init__( self )
		self.__started = None
		self.__finished = None
		assert runner
		self._runner = runner
		self._process = None
		self.__combineOutput = False
		self.__workingDir = None

	def setCombineOutput( self, combine ):
		if combine: # make sure combine is usable as a boolean
			self.__combineOutput = True
		else:
			self.__combineOutput = False

	def getCombineOutput( self ):
		return self.__combineOutput

	def _getRunner( self ):
		return self._runner

	def run( self ):
		self.__started = True
		stderrValue = subprocess.PIPE
		if self.__combineOutput:
			stderrValue = subprocess.STDOUT
		self._process = subprocess.Popen ( self._getRunner().getCommand(), shell = False, cwd = self._getRunner().getWorkingDir(), stdout = subprocess.PIPE, stderr = stderrValue )
		output, error = self._process.communicate()
		self._getRunner()._setStdOut( output )
		self._getRunner()._setStdErr( error )
		self._getRunner()._setReturnCode( self._process.returncode )
		self.__finished = True
		mApp().debugN( self._getRunner(), 5, "STDOUT:\n{0}".format( output ) )
		if not self.__combineOutput:
			mApp().debugN( self._getRunner(), 5, "STDERR:\n{0}".format( error ) )

	def wasStarted( self ):
		return self.__started

	def hasFinished( self ):
		return self.__finished

	def terminate( self ):
		# FIXME logic?
		if self._process:
			self._process.terminate()
		if not self.hasFinished():
			self.join( 5 )
			try:
				self._process.kill()
			except OSError:
				pass # process finished in the meantime (the error is "[Errno 3] No such process")
			self.join( 5 )

class RunCommand( MObject ):
	def __init__( self, cmd, timeoutSeconds = None, combineOutput = False ):
		MObject.__init__( self )
		check_for_list_of_strings( cmd, "The command must be a list of strings." )
		self.__cmd = cmd
		if timeoutSeconds:
			check_for_positive_int( timeoutSeconds, "The timeout period must be a positive integer number! " )
		self.__timeoutSeconds = timeoutSeconds
		self.__workingDir = None
		self.__combineOutput = combineOutput
		self.__stdOut = None
		self.__stdErr = None
		self.__returnCode = None
		self.__timedOut = False

	def getTimeoutSeconds( self ):
		return self.__timeoutSeconds

	def getTimedOut( self ):
		return self.__timedOut

	def setWorkingDir( self, dir ):
		check_for_path( dir, 'The working directory must be a non-empty string!' )
		self.__workingDir = str( dir )

	def getWorkingDir( self ):
		return self.__workingDir

	def getCombineOutput( self ):
		return self.__combineOutput

	def _setReturnCode( self, code ):
		self.__returnCode = code

	def getReturnCode( self ):
		return self.__returnCode

	def _setStdOut( self, stdout ):
		self.__stdOut = stdout

	def getStdOut( self ):
		return self.__stdOut

	def _setStdErr( self, stderr ):
		self.__stdErr = stderr

	def getStdErr( self ):
		return self.__stdErr

	def getCommand( self ):
		return self.__cmd

	def findExecutable( self, program, searchPaths = None ):
		"""Returns path to program found in system's PATH, returns None if nothing found"""

		def isExecutable( fpath ):
			return os.path.exists( fpath ) and os.access( fpath, os.X_OK )

		if searchPaths is None:
			searchPaths = []

		fpath, fname = os.path.split( program )
		if fpath:
			if isExecutable( program ):
				return program
		else:
			paths = searchPaths
			paths += os.environ["PATH"].split( os.pathsep )

			for path in paths:
				executableFile = os.path.join( path, fname )
				if isExecutable( executableFile ):
					return executableFile
				elif sys.platform == "win32" and isExecutable( executableFile + ".exe" ):
					return executableFile + ".exe"

		return None

	def checkVersion( self, parameter = "--version", lineNumber = 0 ):
		"""Check if this command is installed."""
		oldCmd = self.getCommand()
		oldStdOut = self.getStdOut()
		oldStdErr = self.getStdErr()
		oldReturnCode = self.getReturnCode()
		newcmd = [ self.__cmd[0], parameter ]
		self.__cmd = newcmd
		runner = _CommandRunner ( self )
		runner.setCombineOutput( True )
		runner.start()
		runner.join()
		returnCode = self.getReturnCode()
		if returnCode == 0:
			version = self.getStdOut().decode().splitlines()[ lineNumber ].strip()
			mApp().debugN( self, 4, 'RunCommand found: "{0}"'.format( version ) )

		self.__cmd = oldCmd
		self.__stdOut = oldStdOut
		self.__stdErr = oldStdErr
		self.__returnCode = oldReturnCode

		if returnCode != 0:
			raise ConfigurationError( "RunCommand::checkVersion: {0} not found.".format( newcmd[0] ) )

	def run( self ):
		timeoutString = 'without a timeout'
		if self.getTimeoutSeconds() != None:
			timeoutString = 'with timeout of {0} seconds'.format( self.getTimeoutSeconds() )
		combinedOutputString = 'and separate output for stdout and stderr'
		if self.getCombineOutput():
			combinedOutputString = 'and combined stdout and stderr output'
		mApp().debugN( self, 4, 'executing "{0}" {1} {2}'.format( ' '.join( self.getCommand() ), timeoutString, combinedOutputString ) )
		runner = _CommandRunner ( self )
		runner.setCombineOutput( self.getCombineOutput() )
		runner.start()
		# this sucks, but seems to be needed on Windows at least
		while not runner.wasStarted():
			time.sleep( 0.1 )
		if not self.getTimeoutSeconds():
			runner.join()
		else:
			runner.join( self.getTimeoutSeconds() )
		if runner.isAlive():
			runner.terminate()
			runner.join( 5 )
			self.__timedOut = True
		timeoutString = "timed out" if self.getTimedOut() else "completed"
		mApp().debugN( self, 3, '"{0}" {1}, return code is {2}'.format( ' '.join( self.getCommand() ), timeoutString, str( self.getReturnCode() ) ) )
		return self.getReturnCode()
