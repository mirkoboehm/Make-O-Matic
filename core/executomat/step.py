# One step of an executomat run.
# (C) Mirko Boehm, KDAB, 2007
import os, re
from AutobuildCore.helpers.build_script_helpers import DebugN
from AutobuildCore.helpers.exceptdefs import AutoBuildError
from AutobuildCore.helpers.runcommand import RunCommand
from AutobuildCore.Executomat.shellcommand import ShellCommand

class Step( object ):
	"""An individual step of an Executomat run."""
	def __init__( self, stepName = None ):
		self.Enabled = True
		self.__name =stepName
		# the entries in the command lists are not just shell commands, but tuples that contain 
		# * the shell command, and after execution
		# * the return value
		# * the output to stdout and stderr
		# * whether the shello command timed out
		self.PreCommands = [] # list of preparation shell commands
		self.MainCommands = [] # Main Command
		self.PostCommands = [] # Cleanup commands
		self.__logFileName = None
		self.__failed = False
		self.__errorType = 0
		
	def setName( self, n ):
		"""Set the human readable name of the step"""
		self.__name = n

	def name( self ):
		return self.__name

	def setErrorType(self, code):
		self.__errorType = code

	def getErrorType(self):
		return self.__errorType

	def logFileName( self ):
		return self.__logFileName

	def addPreCommand( self, cmdString, workingDir = None, executeOnFailure = False, timeOut = 900 ):
		"""Add one precommand."""
		self.__addCommand( self.PreCommands, cmdString, workingDir, executeOnFailure, timeOut )
		
	def addMainCommand( self, cmdString, workingDir = None, executeOnFailure = False, timeOut = 900 ):
		"""Add a main command."""
		self.__addCommand( self.MainCommands, cmdString, workingDir, executeOnFailure, timeOut )
		
	def addPostCommand( self, cmdString, workingDir = None, executeOnFailure = False, timeOut = 900 ):
		"""Add a post command"""
		self.__addCommand( self.PostCommands, cmdString, workingDir, executeOnFailure, timeOut )

	def __addCommand( self, container, cmdString, workingDir, executeOnFailure, timeOut ):
		cmd = ShellCommand()
		cmd.setWorkingDirectory( workingDir )
		cmd.setCommand( cmdString, timeOut )
		cmd.setExecuteOnFailure( executeOnFailure )
		container.append( cmd ) 
		
	def report( self ):
		"""Generate a human readable report about the command execution.
		Every report is a tuple like this: ( 'stepName', 'ok', 'pre: ok, main: ok, post: ok', 'logFileName.log' )"""
		details = ''
		result = [ self.name(), '', '', self.__logFileName ]
		if not self.Enabled:
			result[1] = 'disabled'
			result[2] = result[1]
			return result
		else:
			workSet = ( ['precmds', '', self.PreCommands ], 
						['maincmds', '', self.MainCommands ], 
						['postcmds', '', self.PostCommands ] )
			notRun = True
			failed = False
			report = ''
			for phase in workSet:
				if not phase[2]: # no commands for this phase
					phase[1] = 'none'
				else:
					for Cmd in phase[2]:
						if not Cmd.executed():
							phase[1] = 'skipped'
							break
						elif Cmd.timedOut():
							phase[1] = 'timeout (failed)'
							failed = True
							notRun = False
							break
						elif Cmd.exitCode() != 0:
							phase[1] = 'failed'
							failed = True
							notRun = False
							break
						else: # success
							notRun = False
							phase[1] = 'ok'
				if result[2]:
					result[2] += ', ' 
				result[2] += phase[0] + ': ' + phase[1]
			if notRun:
				result[1] = 'SKIPPED'
			elif failed:
				result[1] += 'FAILED'
			else:
				result[1] += 'success'
			return result
	
	def execute( self, executomat, weHaveIssues ):
		"""Execute the command"""
		if not self.name():
			raise AutoBuildError( "Cannot execute a command with no name!" )
		if not self.Enabled:
			executomat.log( '# Command ' + self.name() + ' is disabled, skipping.' )
			return True
		executomat.log( '# Executing command "' + self.name() + '"' )
		executomat.log( '# in ' + os.getcwd() )
		DebugN( 5, 'environment before executing ' + self.name() + ':' )
		for key, value in os.environ.iteritems():
			DebugN( 5, '--> ' + key + '   : ' + value )
		Phases = { 'Preparatory Commands' : self.PreCommands, 
				   'Main Commands' : self.MainCommands, 
				   'Post Commands' : self.PostCommands }
		for Phase, CommandList in Phases.iteritems():
			if CommandList:
				executomat.log( '# Executing ' + Phase )
				for Cmd in CommandList:
					if Cmd.workingDirectory():
						executomat.log( '# changing directory to ' + Cmd.workingDirectory() + ' and back' )
					executomat.log( Cmd.command() )
					self.__logFileName = executomat.logDir() + os.sep + re.sub( "\s+", "_", self.name() + '.log' )
					Cmd.setLogFile( self.__logFileName )
					if Cmd.run( weHaveIssues ) == 0:
						executomat.log( '# ' + Phase[:-1] + ' "' + Cmd.command() + '" successful (or skipped)' )
					else:
						executomat.log( '# ' + Phase[:-1] + ' "' + Cmd.command() + '" command failed' )
						self.__failed = True
						return False # do not continue with the remaining commands
		return True
	
	def failed(self):
		return self.__failed

	def setEnabled( self, Enabled ):
		"""Enable the step."""
		self.Enabled = ( Enabled == True )
		
	def enabled( self ):
		"""Return whether this step is enabled."""
		return self.Enabled
