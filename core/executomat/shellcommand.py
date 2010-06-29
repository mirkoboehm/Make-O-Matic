# This file implements the ShellCommand class
import os
from AutobuildCore.helpers.runcommand import RunCommand
from AutobuildCore.helpers.exceptdefs import AutoBuildError

class ShellCommand( object ):
	"""ShellCommand encapsulates the execution of one command in the Step class. 
	It is mostly used internally, but can be of general use as well."""
	def __init__( self ):
		self.__workingDir = None
		self.__executeOnFailure = False
		self.Command = ''
		self.TimeOutPeriod = -1
		self.ExitCode = -1 # default: not started
		self.StdOut = '' # will contain a list of strings
		self.StdErr = '' # same
		self.TimedOut = False
		self.Executed = False # True, after execution
		self.Executed = False
		self.__logFile = ''

	def setLogFile( self, logFile ):
		self.__logFile = logFile
		
	def logFile( self ):
		return self.__logFile

	def setCommand( self, Cmd, TimeOutPeriod = -1 ):
		"""Set the shell command"""
		if not str( Cmd ):
			raise AutoBuildError( 'trying to set a Cmd that is not a string' )
		if TimeOutPeriod < -1:
			raise AutoBuildError( 'invalid timeout period, valid periods are [0..inf) or -1 for no timeout' )
		self.Command = Cmd
		self.TimeOutPeriod = TimeOutPeriod
		self.Executed = False
		
	def command( self ):
		"""Returns the command"""
		return self.Command

	def setWorkingDirectory( self, wDir ):
		"""Set the directory to execute the command in."""
		self.__workingDir = wDir

	def workingDirectory( self ):
		"""Return the working directory."""
		return self.__workingDir

	def setExecuteOnFailure( self, doIt ):
		"""Set execute-on-failure. If true, the command will be executed, even if a previous command of the same sequence failed."""
		self.__executeOnFailure = doIt
	
	def executeOnFailure( self ):
		return self.__executeOnFailure
		
	def run( self, weHaveIssues ):
		"""Executes the shell command. Needs a command to be set."""
		if not self.Command:
			raise AutoBuildError( 'trying to run a command without a command' )
		if weHaveIssues and not self.executeOnFailure(): 
			return 0
		oldCwd = None
		if self.__workingDir:
			if not os.path.isdir( self.__workingDir ):
				raise AutoBuildError( 'working directory ' + self.__workingDir + ' does not exist' )
			oldCwd = os.getcwd()
			os.chdir( self.__workingDir )
		redirect = '' 
		ShellResult = RunCommand( self.Command + redirect, self.TimeOutPeriod, True )
		self.ExitCode = ShellResult[0]
		self.StdOut = ShellResult[1][0]
		self.StdErr = ShellResult[1][1] # should be empty, stdout and stderr are combined
		self.TimedOut = ShellResult[2]
		self.Executed = True
		if self.logFile():
			file = open( self.logFile(), 'a' )
			if file:
				file.writelines( self.stdOut() )
				file.close()
			else: 
				raise AutoBuildError( 'cannot write to log file ' + self.logFile() )
		if oldCwd:
			os.chdir( oldCwd )
		return self.ExitCode
	
	def exitCode( self ):
		"""Returns the shell commands exit code. Can only be called after execution."""
		if not self.Executed:
			raise AutoBuildError( 'exitCode() queried before the command was executed' ) 
		return self.ExitCode
	
	def stdErr( self ):
		"""Returns the stderr output of the command. Can only be called after execution."""
		if not self.Executed:
			raise AutoBuildError( 'stdErr() queried before the command was executed' ) 
		return self.StdErr
	
	def stdOut( self ):
		"""Returns the stderr output of the command. Can only be called after execution."""
		if not self.Executed:
			raise AutoBuildError( 'stdOut() queried before the command was executed' ) 
		return self.StdOut
	
	def timedOut( self ):
		"""Returns True if the shell command process timed out, e.g., was not completed within the timeout period.
		Can only be called after execution."""
		if not self.Executed:
			raise AutoBuildError( 'timedOut() queried before the command was executed' ) 
		return self.TimedOut
	
	def executed( self ):
		"""Returns true if the command has been executed"""
		return self.Executed
