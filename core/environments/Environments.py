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

from core.actions.ExecuteConfigurationBaseAction import ExecuteConfigurationBaseAction
from core.modules.ConfigurationBase import ConfigurationBase
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
import os
from core.Exceptions import MomError
import glob
from core.environments.Dependency import Dependency
from core.environments.Environment import Environment

class Environments( ConfigurationBase ):
	'''Environments is a decorator for Configuration. It takes a configuration, and a list of required folders, and detects matches 
	of the required folders with those found in the environments base directory.
	The configuration is then cloned for every matching environment, if this functionality is enabled for the selected build type.
	'''

	def __init__( self, dependencies = [], name = None, parent = None ):
		ConfigurationBase.__init__( self, name, parent )
		self._setDependencies( dependencies )

	def _setDependencies( self, deps ):
		self.__dependencies = deps

	def addDependency( self, dep ):
		self.__dependencies.append( dep )

	def getDependencies( self ):
		return self.__dependencies

	def _setInstalledDependencies( self, deps ):
		self.__installedDeps = deps

	def _getInstalledDependencies( self ):
		return self.__installedDeps

	def buildConfiguration( self ):
		'''For every environment found during setup, apply the environment, and build the configuration.'''
		error = False
		for environment in self.getChildren():
			if environment.build() != 0:
				error = True
		if error:
			return 1
		else:
			return 0

	def runPreFlightChecks( self ):
		# discover matching environments:
		configs = self.getChildren()[:]
		environments = self.findMatchingEnvironments()
		if environments:
			for config in configs:
				self.removeChild( config )
			for environment in environments:
				environment.cloneConfigurations( configs )
		ConfigurationBase.runPreFlightChecks( self )

	def runSetups( self ):
		try:
			action = ExecuteConfigurationBaseAction( self )
			action.setIgnorePreviousFailure( True ) # there may be multiple configurations
			step = self.getParent().getStep( 'project-build-configurations' )
			step.addMainAction( action )
		except Exception as e:
			print( e )
		ConfigurationBase.runSetups( self )

	def _findMomDependencies( self, folder ):
		"""recursively find leaf nodes within folder"""
		leafNodes = []
		if os.path.isdir( folder ):
			elements = os.listdir( folder )
			for element in elements:
				mApp().debugN( self, 4, 'checking if {0} is a MOM dependency'.format( element ) )
				path = os.path.join( folder, element )
				dependency = Dependency( path )
				if dependency.verify():
					# if self._directoryIsLeafNode( path ):
					leafNodes.append( dependency )
				elif os.path.isdir( path ):
					leafNodes.extend( self._findMomDependencies( path ) )
		return leafNodes

	def _findEnvironmentsForDependencies( self, environmentsRoot, installationNode ):
		"""Returns a path list, looks like that: ( ( EnvPathA1, EnvPathA2, ...), (EnvPathB1, EnvPathB2, ...), ... )
		with one group (list) per dependency
		Returns None if this is no match"""
		descriptions = list( self.getDependencies() ) # make a copy, to avoid modifying the member
		environments = []
		folders = installationNode.split( os.sep )
		root = environmentsRoot.split( os.sep )
		if root != folders[:len( root )]:
			raise MomError( 'The MOM dependency is supposed to be a subfolder of the MOM environments folder!' )
		subTree = folders[len( root ):]
		reversePaths = [ environmentsRoot ]
		current = environmentsRoot
		for folder in subTree:
			current = os.path.join( current, folder )
			reversePaths.append( current )
		reversePaths.reverse()
		mApp().debugN( self, 5, 'incremental paths: {0}'.format( ', '.join( reversePaths ) ) )
		for path in reversePaths:
			os.chdir( path )
			originalDependencies = list( descriptions ) # cannot modify descriptions during iteration
			for pattern in originalDependencies:
				mApp().debugN( self, 3, 'getMatchingPathList: checking for matches to ' + str( pattern ) + ' in ' + str( os.getcwd() ) )
				matches = glob.glob( pattern )
				if len( matches ) > 0:
					leafNodeMatches = []
					for match in matches:
						path = os.path.join( path, match )
						path = os.path.normpath( os.path.abspath( path ) )
						if path in self._getInstalledDependencies():
							leafNodeMatches.append( path )
					if leafNodeMatches:
						leafNodeMatches.sort()
						descriptions.remove( pattern )
						environments.append( leafNodeMatches )
		if len( descriptions ) == 0:
			# uniquify:
			envs = []
			for e in environments:
				if e not in envs:
					envs.append( e )
			return envs
		else:
			return None

	def _addElementsToPathList( self, Environment, PathListCollection, PathList = None ):
		"""perform a depth-first traversal of the tree spanned by the combination of the possible 
		installation paths and create a list of flat lists of directories in PathListCollection"""
		if len( Environment ) > 0:
			Environment[0].sort()
			for Path in Environment[0]:
				NewPathList = [ Path ]
				if PathList != None:
					NewPathList = PathList + NewPathList
				self._addElementsToPathList( Environment[1:], PathListCollection, NewPathList )
		else:
			PathListCollection.append( PathList )

	def _makeNameForPathList( self, PathList ):
		"""take the paths basenames and use them to create a name. easy"""
		Name = ''
		for Path in PathList:
			Parts = Path.split( os.sep )
			if len( Parts ) > 0:
				if len( Name ) != 0:
					Name = Name + ' - '
				Name = Name + Parts[len( Parts ) - 1]
		return Name

	def detectMomDependencies( self ):
		momEnvironmentsRoot = mApp().getSettings().get( Settings.EnvironmentsBaseDir )
		detectedDependencies = self._findMomDependencies( momEnvironmentsRoot )
		deps = {}
		for dep in detectedDependencies:
			folder = os.path.normpath( os.path.abspath( dep.getFolder() ) )
			deps[ folder ] = dep
		self._setInstalledDependencies( deps )
		# mApp().debugN( self, 3, 'found MOM dependencies: {0}'.format( ', '.join( str( detectedDependencies ) ) ) )

	def findMatchingEnvironments( self ):
		# find all leaf nodes:
		momEnvironmentsRoot = mApp().getSettings().get( Settings.EnvironmentsBaseDir )

		if not os.path.isdir( momEnvironmentsRoot ):
			mApp().debug( self, 'warning - MomEnvironments root not found at "{0}". Continuing.'.format( momEnvironmentsRoot ) )
			return []

		mApp().debugN( self, 3, 'MomEnvironments root found at "{0}"'.format( momEnvironmentsRoot ) )
		self.detectMomDependencies()
		# make set of installation nodes
		# FIXME this should be the folders that contain dependencies:
		uniqueDependencyFolders = []
		for dep in self._getInstalledDependencies():
			uniqueDependencyFolders.append( self._getInstalledDependencies()[dep].getContainingFolder() )
		uniqueDependencyFolders = frozenset( uniqueDependencyFolders )
		matchingEnvironments = []
		for dep in uniqueDependencyFolders:
			match = self._findEnvironmentsForDependencies( momEnvironmentsRoot, dep )
			if not match:
				mApp().debugN( self, 3, '{0} has no matching build environment for {1}'
					.format( dep, str( self.getDependencies() ) ) )
			else:
				mApp().debugN( self, 3, '{0} is a matching build environment for {1}'
					.format( dep, str( self.getDependencies() ) ) )
				matchingEnvironments.append( match )
		# pathLists = []
		matchingEnvironments.sort()
# 			for match in matchingEnvironments:
# 				self._addElementsToPathList( match, pathLists )
		environments = []
		for environment in matchingEnvironments:
			env = Environment( 'NoName yet', self )
			for paths in environment:
				for path in paths:
					# FIXME error handling
					dep = self._getInstalledDependencies()[path]
					env.addDependency( dep )
			env.setName( env.makeDescription() )
			environments.append( env )
		return environments

#		for pathList in pathLists:
#			Name = self._makeNameForPathList( pathList )
#			environments.append( [ Name, pathList ] )
#		mApp().debugN( self, 2, 'available build environments for {0}:'.format( str( dependencyDescriptions ) ) )
#		for environment in environments:
#			mApp().debugN( self, 2, str( environment[0] ) + ':' )
#			for path in environment[1]:
#				mApp().debugN( self, 2, '--> ' + path )
#		return environments

	def createXmlNode( self, document ):
		node = document.createElement( "environment" )
		node.attributes["name"] = self.getName()

		return node

	def describe( self, prefix ):
		ConfigurationBase.describe( self, prefix )
		deps = '{0}- dependencies: {1}'.format( prefix, ', '.join( self.getDependencies() ) )
		print( deps )
