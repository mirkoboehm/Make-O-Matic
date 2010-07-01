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
from core.helpers.TypeCheckers import check_for_positive_int

class _CommandRunner( Thread ):
	def __init__ ( self, project, command ):
		Thread.__init__( self )
		self.__project = project
		self.__started = None
		self._cmd = command
		self._output = ()
		self._pid = -1
		self._returnCode = -1
		self._error = ()
		self.__combinedOutput = False

	def getProject( self ):
		return self.__project

	def getReturnCode( self ):
		return self._returnCode

	def setCombinedOutput( self, combine ):
		if combine: # make sure combine is usable as a boolean
			self.__combinedOutput = True
		else:
			self.__combinedOutput = False

	def getCombineOutput( self ):
		return self.__combinedOutput

	def run( self ):
		self.getProject().debugN( 4, 'run_command: ' + self._cmd )
		stderrValue = subprocess.PIPE
		if self.__combinedOutput:
			stderrValue = subprocess.STDOUT
		self.__started = True
		p = Popen ( self._cmd, shell = True, stdout = subprocess.PIPE, stderr = stderrValue )
		self._pid = p.pid
		self._output, self._error = p.communicate()
		self._returnCode = p.returncode
		self.getProject().debugN( 4, 'ReturnCode of run_command: ' + str( p.returncode ) )

	def started( self ):
		return self.__started

	def output( self ):
		return self._output, self._error

	def terminate( self ):
		# FIXME logic?
		if self._pid != -1:
			self.kill( self._pid, signal.SIGTERM )
		if self._pid == True:
			self.join( 5 )
			self.kill( self._pid, signal.SIGKILL )
		self._pid = -1

	def windowskill( self, pid ):
		""" replace os.kill on Windows, where it is not available"""
		cmd = 'taskkill /PID ' + str( int( pid ) ) + ' /T /F'
		if os.system( cmd ) == 0:
			self.getProject().debugN( 4, 'windowskill: process ' + str( pid ) + ' killed.' )

	def kill( self, pid, signal ):
		if 'Windows' in platform.platform():
			self.windowskill( pid )
		else:
			os.kill( pid, signal )

class RunCommand( MObject ):
	def __init__( self, project, cmd, timeoutSeconds = None, combineOutput = False ):
		MObject.__init__( self )
		self.__project = project
		self.__cmd = cmd
		if timeoutSeconds:
			check_for_positive_int( timeoutSeconds, "The timeout period must be a positive integer number! " )
		self.__timeoutSeconds = timeoutSeconds
		self.__combineOutput = combineOutput
		self.__stdOut = ''
		self.__stdErr = ''
		self.__returnCode = None
		self.__timedOut = False

	def getTimeoutSeconds( self ):
		return self.__timeoutSeconds

	def getTimedOut( self ):
		return self.__timedOut

	def getCombineOutput( self ):
		return self.__combineOutput

	def getReturnCode( self ):
		return self.__returnCode

	def getProject( self ):
		return self.__project

	def getStdOut( self ):
		return self.__stdOut

	def getStdErr( self ):
		return self.__stdErr

	def getCommand( self ):
		return self.__cmd

	def run( self ):
		timeoutString = 'without a timeout'
		if self.getTimeoutSeconds() != None:
			timeoutString = 'with timeout of {0} seconds'.format( self.getTimeoutSeconds() )
		combinedOutputString = 'and separate output for stdout and stderr'
		if self.getCombineOutput():
			combinedOutputString = 'and combined stdout and stderr output'
		self.getProject().debugN ( 3, 'run_command: executing "{0}" {1} {2}'.format( self.getCommand(), timeoutString, combinedOutputString ) )
		runner = _CommandRunner ( self.getProject(), self.getCommand() )
		runner.setCombinedOutput( self.getCombineOutput() )
		runner.start()
		# this sucks, but seems to be needed on Windows at least
		while not runner.started():
			time.sleep( 0.1 )
		if not self.getTimeoutSeconds():
			runner.join()
		else:
			runner.join( self.getTimeoutSeconds() )
		if runner.isAlive():
			runner.terminate()
			runner.join( 5 )
			self.__timedOut = True
		self.__stdOut = runner.output()[0]
		self.__stdErr = runner.output()[1]
		self.__returnCode = runner.getReturnCode()
		timeoutString = "timed out" if self.getTimedOut() else "completed"
		self.getProject().debugN( 3, 'command {0}, return code is {1}'.format( timeoutString, str( self.getReturnCode() ) ) )
		return self.getReturnCode()

