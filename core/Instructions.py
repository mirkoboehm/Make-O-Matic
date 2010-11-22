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
from core.helpers.GlobalMApp import mApp
from core.helpers.FilesystemAccess import make_foldername_from_string
from core.Exceptions import ConfigurationError, MomError
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, check_for_nonempty_string
from core.helpers.EnvironmentSaver import EnvironmentSaver
from core.Defaults import Defaults
import os
from core.executomat.Step import Step
from core.Settings import Settings
import traceback

class Instructions( MObject ):
	"""
	Instructions is the base class for anything that can be built by Make-O-Matic.
	* The Build object is a singleton that represents the build script run.
	* Projects are Instructions to build a Project.
	* Configurations are Instructions to build a configuration of a Project.
	* Instructions implement the phased approach to executing the build script, and the 
	idea of plug-ins that implement certain functionality.

	The idea is to have a hierarchical structure like this:

	- Build
	  - Project
	    - Configuration1 (a set of dependencies)
	      - Instruction1.1 (a set of steps including actions, e.g. "./configure")
	      - Instruction1.2
	    - Configuration2
	      - Instruction2.1
	"""

	def __init__( self, name = None, parent = None ):
		MObject.__init__( self, name )
		self._setBaseDir( None )
		self.setParent( None )
		if parent: # the parent instructions object
			parent.addChild( self )
		self.__plugins = []
		self.__instructions = []

	def setParent( self, parent ):
		assert parent == None or isinstance( parent, Instructions )
		self.__parent = parent

	def getParent( self ):
		return self.__parent

	def _setBaseDir( self, folder ):
		check_for_nonempty_string_or_none( folder, 'The instructions base directory must be a folder name, or None!' )
		self.__baseDir = folder

	def getBaseDir( self ):
		check_for_nonempty_string( self.__baseDir, 'basedir can only be queried after preFlightCheck!' )
		return self.__baseDir

	def getPlugins( self ):
		return self.__plugins

	def addPlugin( self, plugin ):
		plugin.setInstructions( self )
		self.__plugins.append( plugin )

	def _getLogDir( self ):
		logDirName = mApp().getSettings().get( Defaults.ProjectLogDir )
		return os.path.join( self.getBaseDir(), logDirName )

	def getChildren( self ):
		return self.__instructions

	def addChild( self, instructions ):
		assert isinstance( instructions, Instructions )
		if instructions in self.getChildren():
			raise MomError( 'A child can be added to the same instruction object only once (offending object: {0})!'
				.format( instructions.getName() ) )
		instructions.setParent( self )
		self.__instructions.append( instructions )

	def removeChild( self, instructions ):
		assert isinstance( instructions, Instructions )
		if instructions in self.getChildren():
			self.getChildren().remove( instructions )
		else:
			raise MomError( 'Cannot remove child {0}, I am not it\'s parent {1}!'
				.format( instructions.getName(), self.getName() ) )

	def execute( self ):
		'''If execute is implemented, it is supposed to execute the pay load of the instructions. 
		Execute is not required, many modules only need to act during the different phases.
		To implement specific operations between setup and wrap-up, re-implement execute.'''
		pass

	def describe( self, prefix ):
		MObject.describe( self, prefix )
		basedir = '(not set)'
		try:
			basedir = self.getBaseDir()
		except ConfigurationError:
			pass
		text = '{0}- base dir: {1}'.format( prefix, basedir )
		print( text )
		subPrefix = prefix + '    '
		for plugin in self.getPlugins():
			plugin.describe( subPrefix )

	def createXmlNode( self, document, recursive = True ):
		node = MObject.createXmlNode( self, document )

		if recursive:
			pluginsElement = document.createElement( "plugins" )
			for plugin in self.getPlugins():
#				#try:
				element = plugin.createXmlNode( document )
#				except Exception as e:
#					element = document.createElement( plugin.getTagName() )
#					element.attributes["name"] = str( plugin.getName() )
#					exceptionNode = create_exception_xml_node( document, e, traceback.format_exc() )
#					element.appendChild( exceptionNode )
				pluginsElement.appendChild( element )
			node.appendChild( pluginsElement )

		return node

	def describeRecursively( self, prefix = '' ):
		'''Describe this instruction object in human readable form.'''
		self.describe( prefix )
		prefix = '    {0}'.format( prefix )
		#print( "LENGTH: {0}".format( len( self.getChildren() ) ) )
		for child in self.getChildren():
			child.describeRecursively( prefix )

	def _setupBuildSteps( self, buildStepsSetting ):
		buildType = mApp().getSettings().get( Settings.ProjectBuildType, True ).lower()
		allBuildSteps = mApp().getSettings().get( buildStepsSetting, True )
		buildSteps = []
		for buildStep in allBuildSteps:
			# FIXME maybe this could be a unit test?
			assert len( buildStep ) == 3
			name, types, ignorePreviousFailure = buildStep
			assert types.lower() == types
			stepName = Step( name )
			stepName.setEnabled( buildType in types )
			stepName.setIgnorePreviousFailure( ignorePreviousFailure )
			buildSteps.append( stepName )
		return buildSteps

	def getIndex( self, instructions ):
		index = 0
		for child in self.getChildren():
			if child == instructions:
				return index
			index = index + 1
		raise MomError( 'Unknown child {0}'.format( instructions ) )

	def _getBaseDirName( self ):
		myIndex = None
		if self.getParent():
			myIndex = self.getParent().getIndex( self ) + 1
		if self.getName() == self.__class__.__name__:
			baseDirName = '{0}'.format( myIndex )
		else:
			index = myIndex or ''
			spacer = '_' if myIndex else ''
			baseDirName = '{0}{1}{2}'.format( index, spacer, make_foldername_from_string( self.getName() ) )
		return baseDirName

	def runPreFlightChecks( self ):
		with EnvironmentSaver():
			mApp().debugN( self, 2, 'performing pre-flight checks' )
			[ plugin.performPreFlightCheck() for plugin in self.getPlugins() ]
			[ child.runPreFlightChecks() for child in self.getChildren() ]

	def runSetups( self ):
		with EnvironmentSaver():
			mApp().debugN( self, 2, 'setting up' )
			[ plugin.performSetup() for plugin in self.getPlugins() ]
			for child in self.getChildren():
				child.runSetups()

	def runWrapups( self ):
		with EnvironmentSaver():
			mApp().debugN( self, 2, 'wrapping up' )
			[ plugin.wrapUp() for plugin in self.getPlugins() ]
			for child in self.getChildren():
				child.runWrapups()

	def runShutDowns( self ):
		with EnvironmentSaver():
			for child in self.getChildren():
				child.runShutDowns()
			mApp().debugN( self, 2, 'shutting down' )
			for plugin in self.getPlugins():
				try:
					plugin.shutDown()
				except Exception as e:
					text = '''\
An error occurred during shutdown: "{0}"
Offending module: "{1}" 
This error will not change the return code of the script!
{2}'''.format( str( e ), plugin.getName(), traceback.format_exc() )
					mApp().message( self, text )

