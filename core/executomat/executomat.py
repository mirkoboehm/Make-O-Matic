# Executomat: A module to execute shell script commands, generate reports on them, 
# and to configure wich steps are actually executed. 
# (C) 2007, Mirko Boehm, KDAB
import os
from step import Step
from AutobuildCore.helpers.exceptdefs import AutoBuildError
from AutobuildCore.helpers.build_script_helpers import DebugN

class Executomat:
	"""Executomat executes shell commands and allows for the simple selection and 
	unselection of individual steps of the commands.
	The shell commands form an ordered list of named steps. Each step consists of
	three phases:
	- Preparation: commands that need to be run before the main command
	- Main Command: this is what it is all about
	- Cleanup: commands that need to be run after the main command.
	Every step can be enabled or disabled individually. If a step is enabled, all 
	of the phases need to finish successfully. If any step fails, the command 
	execution is aborted."""
	
	def __init__( self, name = '' ):
		# Steps contains tuples with the name and the build step
		self.Steps = []
		self.__name = name
		self.__logFile = None
		self.__logFileName = 'execution.log'
		self.__logDir = '.'
		self.__failedStep = None
		
	def setLogDir( self, path ):
		"""Set the directory where all log information is stored."""
		self.__logDir = path
	
	def logDir( self ):
		"""Return the log dir."""
		return self.__logDir

	def setLogFileName( self, filename ):
		"""Set the file to log activity to."""
		self.__logFileName = filename
		
	def logFileName( self ):
		"""Return the log file name."""
		return self.__logFileName
		
	def setName( self, name ):
		"""Store a human readable name for reporting reasons."""
		self.__name = name
		
	def name( self ):
		"""Return the name of the Executomat."""
		return self.__name

	def failed( self ):
		return self.__failedStep != None

	def logFilePathForFailedStep(self):
		if self.__failedStep:
			return self.__failedStep.logFileName()
		
	def addStep( self, step, identifier = None ):
		"""Add a step identified by identifier. If the identifier already exists, the new 
		command replaces the old one."""
		if not isinstance( step, Step ):
			raise AutoBuildError( 'only executomat.Step instances can be added to the queue' )
		Found = False
		if not identifier:
			identifier = step.name()
		for Element in self.Steps:
			if Element[0] == identifier:
				Element[1] == step
				Found = True
		if not Found:
			self.Steps.append( [ identifier, step ] )

	def addCustomCommands( self, command ):
		"""Add a custom command (either a pre, a post command, or both) to a step.
		The command is a tuple ( stepid, precmd, type ). Only one command can added 
		at a time. type is pre or post."""
		if len( command ) != 3 or not str( command[0] ) or not str( command[1] ) or not str( command[2] ):
			raise AutoBuildError( 'Cannot add custom command. Custom commands are tuples ( stepid, command, type), where type is pre or post.' )
		step = self.step( command[0] ) # this may raise an AutoBuildError
		if command[2] == 'pre':
			# add precommand
			pass
		elif command[2] == 'post':
			# add postcommand
			pass
		else:
			# bad
			pass
		assert not 'Implemented'
 
	def step( self, identifier ):
		"""Find the step with this identifier and return it."""
		for element in self.Steps:
			if element[0] == identifier:
				return element[1]
		raise AutoBuildError( 'no such step "' + identifier + '"' )

	def log( self, text ):
		"""Write a text to the log file, if it is there."""
		if( self.__logFile ):
			self.__logFile.write( text.rstrip() + '\n' )
		else:
			DebugN( 1, text )
		
	def run( self, weHaveIssues = False, firstErrorType = -1 ):
		self.__logFile = None
		try:
			if not os.path.isdir( self.logDir() ):
				raise AutoBuildError( 'Log dir at ' + str( self.logDir() ) + ' does not exist.' )
			if self.__logFileName:
				try:
					self.__logFile = open( self.logDir() + os.sep + self.__logFileName, 'a' )
				except:
					raise AutoBuildError( 'Cannot open log file at ' + str( self.__logFileName ) )
			self.log( '# Starting execution of ' + self.name() )
			for Step in self.Steps:
				DebugN( 1, 'now executing step "' + Step[1].name() + '" for "' + self.name() + '"')
				if Step[1].execute( self, weHaveIssues ):
					DebugN( 2, 'success: ' + Step[1].name() )
				else:
					self.log( '# aborting execution except for execute-even-on-failure commands\n########' )
					if firstErrorType == -1:
						firstErrorType = Step[1].getErrorType()
					if self.__failedStep == None:
						# we are only interested in the log files for the first failure 
						self.__failedStep = Step[1]
					weHaveIssues = True # sequence failed
					DebugN( 2, 'failed: ' + Step[1].name() )
			self.log( '# execution finished \n########' )
			return (weHaveIssues, firstErrorType)
		finally: # make sure the log file is closed
			if self.__logFile: 
				self.__logFile.close()

	def report( self ):
		Report = []
		for Step in self.Steps:
			Report.append( Step[1].report() )
		return Report

