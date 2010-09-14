# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2007 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
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
from core.helpers.TypeCheckers import check_for_nonempty_string, check_for_path_or_none
from core.executomat.Step import Step
from core.Exceptions import MomError, ConfigurationError, BuildError
from core.MObject import MObject
from core.helpers.TimeKeeper import TimeKeeper
from core.helpers.GlobalMApp import mApp

class Executomat( MObject ):
	"""Executomat executes actions in steps which can be individually enabled and disabled.
	The operations are performed as an ordered list of named steps. Each step consists of
	three phases:
	- Preparation: actions that need to be run before the main action
	- Main Action: this is what it is all about (for example, "make")
	- Cleanup: Actions that need to be run after the main command.
	Every step can be enabled or disabled individually. If a step is enabled, all 
	of it's actions need to finish successfully."""

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.__steps = []
		self.__timeKeeper = TimeKeeper()
		self.setLogfileName( None )
		self.setLogDir( None )
		self.__logfile = None
		self.__failedStep = None

	def setLogDir( self, path ):
		"""Set the directory where all log information is stored."""
		check_for_path_or_none( path, "The log directory name must be a string containing a path name." )
		self.__logDir = path

	def getLogDir( self ):
		"""Return the log dir."""
		return self.__logDir

	def setLogfileName( self, filename ):
		"""Set the file to log activity to."""
		check_for_path_or_none( filename, "The log file name must be a string containing a path name." )
		self.__logfileName = filename

	def getLogfileName( self ):
		"""Return the log file name."""
		return self.__logfileName

	def hasFailed( self ):
		return self.__failedStep != None

	def logFilePathForFailedStep( self ):
		if self.__failedStep:
			return self.__failedStep.getLogFileName()

	def addStep( self, newStep ):
		"""Add a newStep identified by identifier. If the identifier already exists, the new 
		command replaces the old one."""
		if not isinstance( newStep, Step ):
			raise MomError( 'only executomat.Step instances can be added to the queue' )
		check_for_nonempty_string( newStep.getName(), "Every Executomat step must have a name!" )
		self.__steps.append( newStep )

	def getSteps( self ):
		return self.__steps

	def getStep( self, identifier ):
		"""Find the step with this identifier and return it."""
		for step in self.getSteps():
			if step.getName() == identifier:
				return step
		raise MomError( 'no such step "{0}"'.format( identifier ) )

	def getTimeKeeper( self ):
		return self.__timeKeeper

	def log( self, text ):
		"""Write a text to the log file, if it is there."""
		if( self.__logfile ):
			self.__logfile.write( text.rstrip() + '\n' )

	def run( self, instructions ):
		try:
			self.__timeKeeper.start()
			return self._runTimed( instructions )
		finally:
			self.__timeKeeper.stop()
			mApp().debugN( self, 3, 'duration: {0}'.format( self.__timeKeeper.deltaString() ) )

	def _runTimed( self, instructions ):
		try:
			if not os.path.isdir( self.getLogDir() ):
				raise ConfigurationError( 'Log directory at "{0}" does not exist.'.format( str( self.getLogDir() ) ) )
			if self.getLogfileName():
				try:
					self.__logfile = open( self.getLogDir() + os.sep + self.getLogfileName(), 'a' )
				except:
					raise ConfigurationError( 'Cannot open log file at "{0}"'.format( self.getLogfileName() ) )
			self.log( '# Starting execution of "{0}"'.format( self.getName() ) )
			for step in self.getSteps():
				mApp().debugN( self, 1, 'now executing step "{0}"'.format( step.getName() ) )
				if step.execute( self, instructions ):
					mApp().debugN( self, 2, 'success: "{0}"'.format( step.getName() ) )
					self.log( '# step "{0}": success.'.format( step.getName() ) )
				else:
					self.log( '# step "{0}": ERROR!'.format( step.getName() ) )
					self.log( '# aborting execution except for execute-even-on-failure commands\n########' )
					if self.__failedStep == None:
						# we are only interested in the log files for the first failure 
						self.__failedStep = step
					mApp().registerReturnCode( BuildError( 'dummy' ).getReturnCode() )
					mApp().debugN( self, 2, 'failed: "{0}"'.format( step.getName() ) )
			self.log( '# execution finished \n########' )
		finally: # make sure the log file is closed
			if self.__logfile:
				self.__logfile.close()

	def report( self ):
		report = []
		for step in self.__steps:
			report.append( step[1].report() )
		return report

	def describe( self, prefix ):
		MObject.describe( self, prefix )
		for step in self.getSteps():
			step.describe( prefix + '    ' )
