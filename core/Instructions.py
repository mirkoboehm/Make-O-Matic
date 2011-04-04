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
from core.Exceptions import ConfigurationError, MomError, BuildError
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, check_for_nonempty_string, check_for_path_or_none
from core.executomat.Step import Step
from core.Settings import Settings
from core.helpers.EnvironmentSaver import EnvironmentSaver
import traceback
from copy import deepcopy, copy
from core.helpers.TimeKeeper import TimeKeeper

class Instructions( MObject ):
	"""
	Instructions is the base class for anything that can be built by Make-O-Matic, including the packages and reports locations.
	
	- The Build object is a singleton that represents the build script run.
	- Projects are Instructions to build a Project.
	- Configurations are Instructions to build a configuration of a Project.
	- Instructions implement the phased approach to executing the build script, and the\n
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
		self.setLogDir( None )
		self.setPackagesDir( None )
		self.setParent( None )
		if parent: # the parent instructions object
			parent.addChild( self )
		self.__plugins = []
		self.__instructions = []
		self.__steps = []
		self.__timeKeeper = TimeKeeper()

	def __deepcopy__( self, memo ):
		'''Customize the behaviour of deepcopy to not include the parent object.'''
		# make shallow copy:
		clone = copy( self )
		# plug-ins and instructions need to be deep-copied
		clone.__plugins = deepcopy( self.__plugins, memo )
		for plugin in clone.__plugins:
			plugin.setInstructions( clone )
		clone.__instructions = deepcopy( self.__instructions, memo )
		clone.__timeKeeper = deepcopy( self.__timeKeeper, memo )
		clone.__steps = deepcopy( self.__steps, memo )
		return clone

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

	def setLogDir( self, path ):
		"""Set the directory where all log information is stored."""
		check_for_path_or_none( path, "The log directory name must be a string containing a path name." )
		self.__logDir = path

	def getLogDir( self ):
		"""Return the log directory.
		The log directory is the full path the the location where log output of the step should be saved. It is usually located
		under the log/ sub-directory of the build object, outside of the build tree."""
		return self.__logDir

	def setPackagesDir( self, path ):
		'''Return the packages directory for this object. 
		All data files produced by the build should be stored in the packages directory.'''
		check_for_path_or_none( path, "The packages directory name must be a string containing a path name." )
		self.__packagesDir = path

	def getPackagesDir( self ):
		'''Get the packages directory.'''
		return self.__packagesDir

	def getPlugins( self ):
		return self.__plugins

	def addPlugin( self, plugin ):
		mApp().debugN( self, 4, "Adding plugin: {0}".format( plugin.getName() ) )

		plugin.setInstructions( self )
		self.__plugins.append( plugin )

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

	def getTimeKeeper( self ):
		'''Return the TimeKeeper object to measure execution time.'''
		return self.__timeKeeper

	def getFailedStep( self ):
		'''Return the first step that failed during execution, or None.'''
		for step in self.getSteps():
			if step.getResult() == Step.Result.Failure:
				return step
		return None

	def hasFailed( self ):
		'''Returns True if any action of the build steps for this object has failed.'''
		return self.getFailedStep() != None

	def __hasStep( self, stepName ):
		'''Returns True if a step with the specified name already exists.'''
		try:
			self.getStep( stepName )
			return True
		except MomError:
			return False

	def addStep( self, newStep ):
		"""Add a newStep identified by identifier. If the identifier already exists, the new 
		command replaces the old one."""
		if not isinstance( newStep, Step ):
			raise MomError( 'only Step instances can be added to the queue' )
		check_for_nonempty_string( newStep.getName(), "Every step must have a name!" )
		if self.__hasStep( newStep.getName() ):
			raise MomError( 'A step with the name {0} already exists for this Instructions object!'.format( newStep.getName() ) )
		self.__steps.append( newStep )

	def getSteps( self ):
		'''Return the list of build steps for the object.
		It is a list, not a dictionary, because the steps are a sequence and cannot be reordered.'''
		return self.__steps

	def getStep( self, identifier ):
		"""Find the step with this identifier and return it."""
		for step in self.getSteps():
			if step.getName() == identifier:
				return step
		raise MomError( 'no such step "{0}"'.format( identifier ) )

	def calculateBuildSequence( self ):
		'''Define the build sequence for this object.
		By the default, the build sequence is identical for every BuildInstructions object. Command line parameters that
		enable or disable steps are applied by this method.'''
		buildSteps = self._setupBuildSteps( Settings.ProjectBuildSequence )
		# apply customizations passed as command line parameters:
		mApp().getParameters().applyBuildSequenceSwitches( buildSteps )
		return buildSteps

	def describe( self, prefix, details = None, replacePatterns = True ):
		if not details:
			basedir = '(not set)'
			try:
				basedir = self.getBaseDir()
			except ConfigurationError:
				pass
			details = ' {1}'.format( prefix, basedir )
		super( Instructions, self ).describe( prefix, details, replacePatterns )
		subPrefix = prefix + '    '
		for plugin in self.getPlugins():
			plugin.describe( subPrefix )
		for step in self.getSteps():
				step.describe( prefix + '    ' )

	def createXmlNode( self, document, recursive = True ):
		node = MObject.createXmlNode( self, document )

		node.attributes["timing"] = str( self.getTimeKeeper().deltaString() )
		# FIXME Kevin: better use Step.getStatus() and Step.getResult()
		node.attributes["failed"] = str( self.hasFailed() )

		if recursive:
			# loop through plugins
			pluginsElement = document.createElement( "plugins" )
			for plugin in self.getPlugins():
				element = plugin.createXmlNode( document )
				pluginsElement.appendChild( element )
			node.appendChild( pluginsElement )

		# loop through steps
		stepsElement = document.createElement( "steps" )
		for step in self.getSteps():
			element = step.createXmlNode( document )
			stepsElement.appendChild( element )
		node.appendChild( stepsElement )

		return node

	def describeRecursively( self, prefix = '' ):
		'''Describe this instruction object in human readable form.'''
		self.describe( prefix )
		prefix = '    {0}'.format( prefix )
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


	def runPrepare( self ):
		with EnvironmentSaver():
			mApp().debugN( self, 2, 'preparing' )
			self.prepare()
			[ plugin.performPrepare() for plugin in self.getPlugins() ]
			[ child.runPrepare() for child in self.getChildren() ]


	def runPreFlightChecks( self ):
		with EnvironmentSaver():
			mApp().debugN( self, 2, 'performing pre-flight checks' )
			self.preFlightCheck()
			[ plugin.performPreFlightCheck() for plugin in self.getPlugins() ]
			[ child.runPreFlightChecks() for child in self.getChildren() ]

	def runSetups( self ):
		with EnvironmentSaver():
			mApp().debugN( self, 2, 'setting up' )
			self.setup()
			[ plugin.performSetup() for plugin in self.getPlugins() ]
			[ child.runSetups() for child in self.getChildren() ]

	def runExecute( self ):
		with EnvironmentSaver():
			mApp().debugN( self, 2, 'executing' )
			self.execute()
			[ child.execute() for child in self.getChildren() ]

	def _stepsShouldExecute( self ):
		'''Return if the steps should be executed for this object. 
		By default, steps should be executed if no error happened so far. Steps with the execute-on-failure property set to True
		will execute even if this method returns False.'''
		return mApp().getReturnCode() == 0

	def _executeStepRecursively( self, instructions, name ):
		'''Execute one step of the build sequence recursively, for this object, and all child objects.'''
		self.executeStep( name )
		for child in instructions.getChildren():
			child._executeStepRecursively( child, name )

	def executeStep( self, stepName ):
		'''Execute one individual step.
		This method does not recurse to child objects.'''

		mApp().debug( self, "Executing step: {0}".format( stepName ) )
		step = self.getStep( stepName )
		try:
			if not step.execute( self ):
				mApp().registerReturnCode( BuildError( 'dummy' ).getReturnCode() )
		finally:
			if not step.isEmpty():
				noOfActions = len( step.getPreActions() ) + len( step.getMainActions() ) + len( step.getPostActions() )
				mApp().debug( self, '{0}: actions: {1}, status: {2}, result: {3}, duration: {4}'.format( 
					step.getName(),
					noOfActions,
					Step.Status.getDescription( step.getStatus() ),
					Step.Result.getDescription( step.getResult() ),
					step.getTimeKeeper().deltaString() ) )

	def runWrapups( self ):
		with EnvironmentSaver():
			mApp().debugN( self, 2, 'wrapping up' )
			[ plugin.wrapUp() for plugin in self.getPlugins() ]
			for child in self.getChildren():
				child.runWrapups()

	def runShutDowns( self ):
		with EnvironmentSaver():
			self.shutDown()
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


	def prepare( self ):
		'''Execute the prepare phase for this object.'''
		pass

	def preFlightCheck( self ):
		'''Execute the pre-flight check phase for this object.'''
		pass

	def setup( self ):
		'''Execute the setup phase for this object.'''
		pass

	def execute( self ):
		'''Execute the execute phase for this object.
		If execute is implemented, it is supposed to execute the pay load of the instructions. 
		Execute is not required, many modules only need to act during the different phases.
		To implement specific operations between setup and wrap-up, re-implement execute.'''
		pass

	def wrapup( self ):
		'''Execute the wrapup phase for this object.'''
		pass

	def shutDown( self ):
		'''Execute the shut down phase for this object.'''
		pass
