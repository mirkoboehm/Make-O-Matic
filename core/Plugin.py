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
from core.Exceptions import MomException
from core.helpers.GlobalMApp import mApp
from core.helpers.RunCommand import RunCommand

class Plugin( MObject ):

	def __init__( self, name = None ):
		"""Constructor"""
		MObject.__init__( self, name )
		self.setEnabled( True )
		self.setOptional( False )
		self.setInstructions( None )
		self.__command = None
		self.__commandSearchPaths = None

	def setInstructions( self, instructions ):
		'''Assign this plugin to it's instruction object. 
		This method is called automatically during addPlugin.'''

		self.__instructions = instructions

	def getInstructions( self ):
		return self.__instructions

	def getTagName( self ):
		return "plugin"

	def performPreFlightCheck( self ):
		'''This method handles the execution of the pre flight check. Do not overload this method to adapt it, overload 
		preFlightCheck instead!'''
		if not self.isEnabled():
			mApp().debugN( self, 2, 'this plugin is disabled, skipping pre flight check.' )
			return
		try:
			self.preFlightCheck()
		except MomException as e:
			if self.getOptional():
				mApp().message( self, 'pre flight check failed, disabling the plugin because it is marked as optional.' )
				self.setEnabled( False )
			else:
				raise e

	def preFlightCheck( self ):
		"""PreFlightCheck is called after the command line arguments have been passed, 
		but before the build steps are generated.
		Modules should check the setup of the tools they use in this phase.
		If any error occurs that prevents the plugin from working properly, the method should throw a ConfigurationError 
		exception."""
		if self.getCommand():
			RunCommand( [ self.getCommand() ] ).checkVersion()

	def performSetup( self ):
		'''This method handles the execution of the setup phase. Do not overload this method to adapt it, overload 
		setup instead!'''
		if self.isEnabled():
			self.setup()
		else:
			mApp().debugN( self, 2, 'this plugin is disabled, not generating any actions.' )

	def setup( self ):
		"""Setup is called after the build steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		pass

	def wrapUp( self ):
		"""WrapUp is called when the last step has finished. It could be used to publish 
		the reports, for example."""
		pass

	def shutDown( self ):
		"""Shutdown is called right before the build ends. It could be used to close
		files or network connections.
		ShutDown is called from the finally block of the build method, so in all normal cases, it will be called 
		before the build script ends."""
		pass

	def getCommand( self ):
		return self.__command

	def _setCommand( self, command, searchPaths = None ):
		self.__command = RunCommand( [ command ], None, False, searchPaths ).getCommand()[0]

	def setEnabled( self, onOff ):
		self.__enabled = onOff

	def isEnabled( self ):
		return self.__enabled

	def setOptional( self, onOff ):
		self.__optional = onOff

	def getOptional( self ):
		return self.__optional

	def getXmlTemplate( self, element, wrapper ):
		"""Returns a string representing the information about this plugin
		
		Parameter element is an instance of Element,
		parameter wrapper an instance of textwrap.TextWrapper
		
		Overwrite if necessary, returns None by default"""

		# pylint: disable-msg=W0613

		return None

	def getXslTemplates( self ):
		"""Returns a dict of XML templates for this plugin. See ConsoleLogger method overwrite for example.
		
		Overwrite if necessary, returns an empty dict by default"""

		return {}

