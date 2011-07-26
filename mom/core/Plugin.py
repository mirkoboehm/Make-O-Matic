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

from copy import deepcopy, copy
from mom.core.Exceptions import MomException, ConfigurationError
from mom.core.MObject import MObject
from mom.core.helpers.GlobalMApp import mApp
from mom.core.helpers.RunCommand import RunCommand
from mom.core.helpers.TypeCheckers import check_for_nonempty_string, check_for_list_of_paths
import os.path
from mom.core.helpers.XmlUtils import create_child_node

class Plugin( MObject ):
	"""
	Plugins implement specific functionality, for example to integrate a tool like Doxygen into the build script run.
	They encapsulate all the integration code for a specific purpose,
	so that build scripts are modular and only check for the tools that are required for the build.

	\section additional Additional information
	Plugins are added to instruction objects. Some plugins are specific to Build, Project, or Configuration instructions objects.

	The execution during a build run is split into several phases, see Build documentation

	\section reports Reporting functionality
	Each plugin can provide a short textual description which is shown in all report formats
	\see getObjectStatus

	\subsection plain-text Plain text
	Each plugin can register its own templating function which will be shown in the plain text output
	\see getXmlTemplate

	\subsection others Others
	Each plugin can register its own XSL templates using the following functions
	\see getXslTemplates"""

	_PLUGIN_DATA_DIR = os.path.join( os.path.dirname( __file__ ), "plugins/data" )

	def __init__( self, name = None ):

		MObject.__init__( self, name )
		self.setEnabled( True )
		self.setOptional( False )
		self.setInstructions( None )
		self.__command = None
		self.__commandArguments = []
		self.__commandSearchPaths = []

	def __deepcopy__( self, memo ):
		clone = copy( self )
		clone.__command = deepcopy( self.__command, memo )
		clone.__commandArguments = deepcopy( self.__commandArguments, memo )
		clone.__commandSearchPaths = deepcopy( self.__commandSearchPaths, memo )
		return clone

	def setInstructions( self, instructions ):
		'''Assign this plugin to it's instruction object.

		This method is called automatically during addPlugin.'''

		self.__instructions = instructions

	def getInstructions( self ):
		return self.__instructions

	def getTagName( self ):
		return "plugin"

	def getPluginType( self ):
		return "general"

	def performPrepare( self ):
		'''This message controls the execution of the prepare phase.
		It should not be overloaded. Overload prepare() instead.'''
		self.prepare()

	def prepare( self ):
		'''Perform the prepare phase.
		In the prepare phase, plug-ins are allowed to manipulate settings, and apply changes to the
		build tree. The pre-flight check is performed after this phase, so plugins should be prepared
		that setup errors can happen.'''
		pass

	def resolveCommand( self ):
		# if no command specified, do not run check
		if not self.getCommand():
			return

		runCommand = RunCommand( [ self.getCommand() ], searchPaths = self.__commandSearchPaths )
		runCommand.checkVersion()

	def performPreFlightCheck( self ):
		'''This method handles the execution of the pre flight check.

		Do not overload this method to adapt it, overload preFlightCheck instead ! '''

		if not self.isEnabled():
			mApp().debugN( self, 2, 'this plugin is disabled, skipping pre flight check.' )
			return

		def findCommandAndPreFlightCheck():
			if self.getCommand():
				self.resolveCommand()
			self.preFlightCheck()

		if self.isOptional():
			try:
				findCommandAndPreFlightCheck()
			except ( MomException, ConfigurationError ), e:
				mApp().message( self, 'pre flight check failed, disabling the plugin because it is marked as optional: {0}'.format( e ) )
				self.setObjectDescription( unicode( e ) )
				self.setEnabled( False )
		else:
			findCommandAndPreFlightCheck()

	def preFlightCheck( self ):
		"""PreFlightCheck is called after the command line arguments have been passed,
		but before the build steps are generated.

		Modules should check the setup of the tools they use in this phase.

		If any error occurs that prevents the plugin from working properly, the method should throw a ConfigurationError
		exception."""
		pass

	def performSetup( self ):
		'''This method handles the execution of the setup phase.

		Do not overload this method to adapt it, overload setup instead ! '''

		if not self.isEnabled():
			mApp().debugN( self, 2, 'this plugin is disabled, not generating any actions.' )
			return

		self.setup()

	def setup( self ):
		"""Setup is called after the build steps have been generated, and the command line
		options have been applied to them.

		It can be used to insert actions into the build steps, for example."""
		pass

	def wrapUp( self ):
		"""WrapUp is called when the last step has finished.

		It could be used to publish the reports, for example."""
		pass

	def performReport( self ):
		if not self.isEnabled():
			mApp().debugN( self, 2, 'this plug-in is disabled, not not creating reports' )
			return

		self.report()

	def report( self ):
		"""Report is called after the build has finished. Plug-ins that generate reports
		about the build should overload this method."""
		pass

	def performNotify( self ):
		if not self.isEnabled():
			mApp().debugN( self, 2, 'this plug-in is disabled, skipping notifications' )
			return

		self.notify()

	def notify( self ):
		"""Send out notifications about the build process. Plug-ins that, for example, send
		emails, create chat notifications or talk to remote servers should overload this
		method."""
		pass

	def shutDown( self ):
		"""Shutdown is called right before the build ends.

		It could be used to close files or network connections.

		\note shutDown() is called from the finally block of the build method, so in all normal cases, it will be called
		before the build script ends."""
		pass

	def _setCommandArguments( self, commandArguments ):
		check_for_list_of_paths( commandArguments, "Must be a list of strings or PathResolver objects" )
		self.__commandArguments = commandArguments

	def getCommandArguments( self ):
		return self.__commandArguments

	def getCommandWithArguments( self ):
		cmd = [ self.getCommand() ]
		cmd += [str( x ) for x in self.getCommandArguments()] # str() evaluates the PathResolver objects
		return cmd

	def _setCommandSearchPaths( self, searchPaths ):
		if searchPaths is None:
			searchPaths = []
		check_for_list_of_paths( searchPaths, "The search paths need to be a list of file system paths." )
		self.__commandSearchPaths = searchPaths

	def getCommandSearchPaths( self ):
		return self.__commandSearchPaths

	def getCommand( self ):
		return self.__command

	def _setCommand( self, command ):
		check_for_nonempty_string( command, "The command needs to be a non-empty string." )
		self.__command = command

	def setEnabled( self, onOff ):
		self.__enabled = onOff

	def isEnabled( self ):
		return self.__enabled

	def setOptional( self, onOff ):
		self.__optional = onOff

	def isOptional( self ):
		return self.__optional

	@classmethod
	def setDefaultSetting( cls, name, value ):
		"""Call this to set a default settings of a plugin, does nothing if name already exists in settings"""

		try:
			cls.getSetting( name, True )
		except ConfigurationError:
			cls.setSetting( name, value )

	@classmethod
	def setSetting( cls, name, value ):
		"""Call this to save settings of a plugin, do not use Settings class directly!"""

		mApp().getSettings().set( "plugin.{0}.{1}".format( cls.__name__ , name ), value )

	@classmethod
	def getSetting( cls, name, required = True ):
		"""Call this to load settings from a plugin, do not use Settings class directly!"""

		return mApp().getSettings().get( "plugin.{0}.{1}".format( cls.__name__ , name ), required )

	def createXmlNode( self, document ):
		node = super( Plugin, self ).createXmlNode( document )

		node.attributes["isEnabled"] = str( self.isEnabled() )
		node.attributes["isOptional"] = str( self.isOptional() )
		node.attributes["pluginType"] = str( self.getPluginType() )

		return node

	def getXmlTemplate( self, element, wrapper ):
		"""Returns a string representing the information about this plugin

		\param element is an instance of Element,
		\param wrapper an instance of textwrap.TextWrapper

		\note Overwrite if necessary, returns None by default"""

		# pylint: disable-msg=W0613

		return None

	def getXslTemplates( self ):
		"""Returns a dict of XML templates for this plugin. See ConsoleLogger method overwrite for example.

		\note Overwrite if necessary, returns an empty dict by default"""

		return {}
