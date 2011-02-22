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

from core.ConfigurationBase import ConfigurationBase
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
import os
from core.Exceptions import MomError, ConfigurationError
from core.environments.Dependency import Dependency
from fnmatch import fnmatch
from core.environments.Environment import Environment

class Environments( ConfigurationBase ):
	'''Environments is a decorator for Configuration. It takes a configuration, and a list of required folders, and detects matches 
	of the required folders with those found in the environments base directory.
	The configuration is then cloned for every matching environment, if this functionality is enabled for the selected build type.
	'''

	def __init__( self, dependencies = None, name = None, parent = None ):
		'''Constructor.'''
		ConfigurationBase.__init__( self, name, parent )
		self._setDependencies( dependencies )
		if dependencies:
			self.setObjectStatus( "Dependencies: {0}".format( ", ".join( dependencies ) ) )
		self.setOptional( False )

	def _setDependencies( self, deps ):
		'''Set the list of dependencies. A match must be found for every listed dependency for the child 
		configurations to be built. The dependencies are shell patterns that are looked for in the Make-O-Matic packages folder.'''
		self.__dependencies = deps

	def addDependency( self, dep ):
		'''Add a dependency.'''
		self.__dependencies.append( dep )

	def getDependencies( self ):
		'''Return the dependencies.'''
		return self.__dependencies

	def _setInstalledDependencies( self, deps ):
		self.__installedDeps = deps

	def _getInstalledDependencies( self ):
		return self.__installedDeps

	def setOptional( self, onOff ):
		'''Mark the environments as optional.
		By default, the build is aborted if no environment can be found in which the configurations can be built. If the 
		environment is optional and no matches are found, the configurations will not be built, but no error is raised.'''
		self.__optional = onOff

	def isOptional( self ):
		'''Return if this environment is optional.'''
		return self.__optional

	def __selectBestScoringEnvironment( self, environments ):
		assert len( environments ) > 0
		decoratedTuples = []
		index = 0
		for env in environments:
			scores = []
			for dep in env.getDependencies():
				scores.append( dep.getScore() )
			decoratedTuples.append( [ scores, index, env ] )
			index += 1
		decoratedTuples.sort( reverse = True )
		return decoratedTuples[0][2]

	def __expandConfigurations( self, configs, environments ):
		for config in configs:
			self.removeChild( config )
		for environment in environments:
			environment.cloneConfigurations( configs )

	def prepare( self ):
		'''Prepare method, overloaded.'''
		# discover matching environments:
		buildType = mApp().getSettings().get( Settings.ProjectBuildType, True ).lower()
		runMode = mApp().getSettings().get( Settings.ScriptRunMode )
		# FIXME (Kevin, what do you think?) this may have to be a property, so that the expansion mode can be added to the build report 
		mode = Settings.EnvironmentExpansionMode_Ignore
		if buildType in mApp().getSettings().get( Settings.EnvironmentsExpansionModeMapping ):
			mode = mApp().getSettings().get( Settings.EnvironmentsExpansionModeMapping )[ buildType ]
		description = Settings.EnvironmentsExpansionModes[ mode ]
		mApp().debugN( self, 2, 'Environment expansion mode for build type {0} is "{1}"'.format( buildType, description ) )
		configs = self.getChildren()[:]
		environments = self.findMatchingEnvironments()
		if mode in ( Settings.EnvironmentExpansionMode_BuildAll, Settings.EnvironmentExpansionMode_BuildHighestScoring ):
			if not environments:
				status = 'optional' if self.isOptional() else 'REQUIRED'
				self.setObjectStatus( 'No environments found [{0}]'.format( status ) )
				mApp().message( self, self.getObjectStatus() )
				if self.isOptional():
					mApp().message( self, '{0}, continuing.'.format( self.getObjectStatus() ) )
				else:
					if runMode == Settings.RunMode_Build:
						details = 'Missing environment: {0}'.format( ', '.join( self.getDependencies() ) )
						raise ConfigurationError( 'No environment found that matches the project requirements!', details )
			if mode == Settings.EnvironmentExpansionMode_BuildHighestScoring and environments:
				environment = self.__selectBestScoringEnvironment( environments )
				mApp().debugN( self, 2, 'best scoring environment is "{0}" (out of {1})'
					.format( environment.makeDescription(), len( environments ) ) )
				environments = [ environment ]
			self.__expandConfigurations( configs, environments )
		elif mode == Settings.EnvironmentExpansionMode_Ignore:
			mApp().debugN( self, 2, 'environments will not be applied in build type {0}'.format( buildType ) )
		else:
			# should not happen
			raise MomError( 'The environment mode {0} is undefined!'.format( mode ) )
		super( Environments, self ).prepare()

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

	def detectMomDependencies( self ):
		'''Detect all mom dependency packages in the configured base directory.'''
		momEnvironmentsRoot = mApp().getSettings().get( Settings.EnvironmentsBaseDir )
		detectedDependencies = self._findMomDependencies( momEnvironmentsRoot )
		deps = {}
		for dep in detectedDependencies:
			folder = os.path.normpath( os.path.abspath( dep.getFolder() ) )
			deps[ folder ] = dep
		self._setInstalledDependencies( deps )

	def __calculateMatches( self, packages, remainingDependencies, folders ):
		'''Recursively find the matches for this environment.'''
		matches = []
		if not folders:
			return None

		mApp().debugN( self, 3, 'trying to find matching environments for {0}'.format( ", ".join( self.getDependencies() ) ) )
		folder = folders[0]
		for dep in remainingDependencies:
			for item in os.listdir( folder ):
				path = os.path.join( folder, item )
				if not os.path.isdir( path ):
					continue
				if fnmatch( item, dep ):
					if path not in self._getInstalledDependencies():
						mApp().debugN( self, 4, 'dependency {0} matches, but is not enabled'.format( item ) )
						continue
					newPackages = list( packages )
					newPackages.append( [ path, dep ] )
					newDeps = list( self.getDependencies() )
					newDeps.remove( dep )
					if newDeps:
						# there are still dependencies to find further up the path
						theseMatches = self.__calculateMatches( newPackages, newDeps, folders[1:] )
						if theseMatches:
							matches.append( theseMatches )
					else:
						# yay, all dependencies have been found
						matches.append( newPackages )
				else:
					mApp().debugN( self, 4, 'dependency {0} does not match {1}'.format( item, dep ) )
		return matches

	def __ensureDependencyOrder( self, unsortedMatches, dependencies ):
		matches = []
		for match in unsortedMatches:
			assert len( match ) == len( dependencies )
			sortedMatch = []
			for dep in dependencies:
				for element in match:
					if element[1] == dep:
						sortedMatch.append( element[ 0 ] )
			assert len( sortedMatch ) == len( match )
			matches.append( sortedMatch )
		return matches

	def findMatchingEnvironments( self ):
		'''Find and return all matches for the specified dependencies.'''
		# find all leaf nodes:
		momEnvironmentsRoot = mApp().getSettings().get( Settings.EnvironmentsBaseDir )

		if not os.path.isdir( momEnvironmentsRoot ):
			mApp().debug( self, 'warning - MomEnvironments root not found at "{0}". Continuing.'.format( momEnvironmentsRoot ) )
			return []

		mApp().debugN( self, 3, 'MomEnvironments root found at "{0}"'.format( momEnvironmentsRoot ) )
		self.detectMomDependencies()
		# make set of installation nodes
		uniqueDependencyFolders = []
		for dep in self._getInstalledDependencies():
			uniqueDependencyFolders.append( self._getInstalledDependencies()[dep].getContainingFolder() )
		uniqueDependencyFolders = frozenset( uniqueDependencyFolders )
		allRawEnvironments = [] # these are the folders, that will be converted to Environment objects later
		for folder in uniqueDependencyFolders:
			# calculate the paths to look at
			folders = folder.split( os.sep )
			root = momEnvironmentsRoot.split( os.sep )
			if root != folders[:len( root )]:
				raise MomError( 'The MOM dependency is supposed to be a sub directory of the MOM environments folder!' )
			subTree = folders[len( root ):]
			reversePaths = [ momEnvironmentsRoot ]
			current = momEnvironmentsRoot
			for folder in subTree:
				current = os.path.join( current, folder )
				reversePaths.append( current )
			reversePaths.reverse()
			mApp().debugN( self, 5, 'incremental paths: {0}'.format( ', '.join( reversePaths ) ) )
			matches = self.__calculateMatches( [], list( self.getDependencies() ), reversePaths )
			if matches:
				sortedMatches = self.__ensureDependencyOrder( matches, self.getDependencies() )
				allRawEnvironments.extend( sortedMatches )
		# convert to Environment objects, make them unique, because the matching algorithm potentially finds duplicates:
		environments = []
		for env in allRawEnvironments:
			envs = []
			for path in env:
				envs.append( self._getInstalledDependencies()[ path ] )
			envs = frozenset( envs )
			match = Environment( parent = self )
			match.setDependencies( envs )
			match.setName( match.makeDescription() )
			environments.append( match )
		environments = frozenset( environments )
		return environments

	def createXmlNode( self, document ):
		node = super( Environments, self ).createXmlNode( document )
		node.attributes["isOptional"] = str( self.isOptional() )
		node.attributes["isEnabled"] = str( self.getChildren() > 0 ) # no configurations as children => disabled
		return node
