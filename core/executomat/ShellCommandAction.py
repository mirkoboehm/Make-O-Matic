# This file implements the ShellCommandAction class
import os
from core.helpers.TypeCheckers import check_for_nonempty_string, check_for_nonnegative_int
from core.Exceptions import MomError
from core.helpers.RunCommand import RunCommand
from core.executomat.Action import Action

class ShellCommandAction( Action ):
	"""ShellCommandAction encapsulates the execution of one command in the Step class. 
	It is mostly used internally, but can be of general use as well."""
	def __init__( self, command = None, timeout = None, workingDir = None ):
		Action.__init__( self )
		self.setCommand( command, timeout )
		if workingDir:
			self.setWorkingDirectory( workingDir )
		self.__runner = None

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return self.getName()

	def setCommand( self, command, TimeOutPeriod = None ):
		"""Set the shell command"""
		check_for_nonempty_string( command, 'trying to set a command that is not a string' )
		if TimeOutPeriod != None:
			check_for_nonnegative_int( TimeOutPeriod, 'invalid timeout period, valid periods are [0..inf) or None for no timeout' )
		self.__command = command
		self.__timeOutPeriod = TimeOutPeriod

	def getCommand( self ):
		"""Returns the command"""
		return self.__command

	def _getRunner( self ):
		if self.__runner == None:
			raise MomError( "The command runner was not initialized before being queried" )
		return self.__runner

	def run( self, project ):
		"""Executes the shell command. Needs a command to be set."""
		check_for_nonempty_string( self.getCommand(), 'trying to run a command without a command' )
		if project.getReturnCode() != 0 and not self.executeOnFailure():
			return 0
		oldCwd = None
		try:
			if self.getWorkingDirectory():
				if not os.path.isdir( self.getWorkingDirectory() ):
					raise MomError( 'working directory ' + self.__workingDir + ' does not exist' )
				oldCwd = os.getcwd()
				os.chdir( self.getWorkingDirectory() )
			self.__runner = RunCommand( project, self.__command, self.__timeOutPeriod, True )
			self._getRunner().run()
			if self.getLogfileName():
				file = open( self.getLogfileName(), 'a' )
				if file:
					file.writelines( self._getRunner().getStdOut().decode() )
					file.close()
				else:
					raise MomError( 'cannot write to log file "{0}"'.format( self.getLogfileName() ) )
		finally:
			if oldCwd:
				os.chdir( oldCwd )
		return self._getRunner().getReturnCode() == 0

	def hasTimedOut( self ):
		"""Returns True if the shell command process timed out, e.g., was not completed within the timeout period.
		Can only be called after execution."""
		if not self.__started:
			raise MomError( 'timedOut() queried before the command was executed' )
		return self._getRunner().getTimedOut();

