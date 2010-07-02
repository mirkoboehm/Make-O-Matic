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
from threading import Thread
import platform
import subprocess
from subprocess import Popen
import signal
import time
from core.MObject import MObject
from core.helpers.TypeCheckers import check_for_positive_int, check_for_nonempty_string
import core

class _CommandRunner( Thread ):
	def __init__ ( self, project, runner ):
		Thread.__init__( self )
		self.__project = project
		self.__started = None
		self.__finished = None
		assert runner
		self._runner = runner
		self._pid = None
		self.__combineOutput = False

	def getProject( self ):
		return self.__project

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
		self.getProject().debugN( self._getRunner(), 4, 'executing "{0}"'.format( self._getRunner().getCommand() ) )
		stderrValue = subprocess.PIPE
		if self.__combineOutput:
			stderrValue = subprocess.STDOUT
		self.__started = True
		p = Popen ( self._getRunner().getCommand(), shell = True, stdout = subprocess.PIPE, stderr = stderrValue )
		self._pid = p.pid
		output, error = p.communicate()
		self._getRunner()._setStdOut( output )
		self._getRunner()._setStdErr( error )
		self._getRunner()._setReturnCode( p.returncode )
		self.__finished = True
		self.getProject().debugN( self, 4, 'finished, return code {0}'.format( p.returncode ) )

	def wasStarted( self ):
		return self.__started

	def hasFinished( self ):
		return self.__finished

	def terminate( self ):
		# FIXME logic?
		if self._pid:
			self.kill( self._pid, signal.SIGTERM )
		if not self.hasFinished():
			self.join( 5 )
			self.kill( self._pid, signal.SIGKILL )
			self.join( 5 )
		self._pid = -1

	def windowskill( self, pid ):
		""" replace os.kill on Windows, where it is not available"""
		cmd = 'taskkill /PID ' + str( int( pid ) ) + ' /T /F'
		if os.system( cmd ) == 0:
			self.getProject().debugN( self, 4, 'windows-kill killed process {0}'.format( pid ) )

	def kill( self, pid, signal ):
		if 'Windows' in platform.platform():
			self.windowskill( pid )
		else:
			os.kill( pid, signal )

class RunCommand( MObject ):
	def __init__( self, project, cmd, timeoutSeconds = None, combineOutput = False ):
		MObject.__init__( self )
		assert isinstance( project, core.Project.Project )
		self.__project = project
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
		check_for_nonempty_string( dir, 'The working directory must be a non-empty string!' )
		self.__workingDir = dir

	def getWorkingDir( self ):
		return self.__workingDir

	def getCombineOutput( self ):
		return self.__combineOutput

	def _setReturnCode( self, code ):
		self.__returnCode = code

	def getReturnCode( self ):
		return self.__returnCode

	def getProject( self ):
		return self.__project

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

	def run( self ):
		oldCwd = None
		try:
			if self.getWorkingDir():
				oldCwd = os.getcwd()
				os.chdir( self.getWorkingDir() )
			timeoutString = 'without a timeout'
			if self.getTimeoutSeconds() != None:
				timeoutString = 'with timeout of {0} seconds'.format( self.getTimeoutSeconds() )
			combinedOutputString = 'and separate output for stdout and stderr'
			if self.getCombineOutput():
				combinedOutputString = 'and combined stdout and stderr output'
			self.getProject().debugN( self, 3, 'executing "{0}" {1} {2}'.format( self.getCommand(), timeoutString, combinedOutputString ) )
			runner = _CommandRunner ( self.getProject(), self )
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
			self.getProject().debugN( self, 3, 'command {0}, return code is {1}'.format( timeoutString, str( self.getReturnCode() ) ) )
			return self.getReturnCode()
		finally:
			if oldCwd:
				os.chdir( oldCwd )

