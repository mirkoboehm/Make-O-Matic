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
import re
from core.Exceptions import ConfigurationError
import glob
import fnmatch

class Environments( ConfigurationBase ):
	'''Environments is a decorator for Configuration. It takes a configuration, and a list of required folders, and detects matches 
	of the required folders with those found in the environments base directory.
	The configuration is then cloned for every matching environment, if this functionality is enabled for the selected build type.
	'''

	def __init__( self, dependencies = None, name = None, parent = None ):
		ConfigurationBase.__init__( self, name, parent )
		self._setDependencies( dependencies )

	def _setDependencies( self, deps ):
		self.__dependencies = deps

	def getDependencies( self ):
		return self.__dependencies

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
		# [ Environment( 'Qt-4.6.2-Shared-Release', self ) ] # FIXME
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
			step = self.getParent().getExecutomat().getStep( 'project-build-configurations' )
			step.addMainAction( action )
		except Exception as e:
			print( e )
		ConfigurationBase.runSetups( self )

	def _readControlFile( self, controlFile ):
		mApp().debugN( self, 2, 'loading settings from package control file "{0}"'.format( str ( controlFile ) ) )
		try:
			packageEnabled = False
			commands = []
			for line in open( controlFile, 'r' ).readlines():
				if re.match( '^\s*#', line ): continue # ignore comments
				if re.match( '^\s*$', line ): continue # ignore empty lines
				if re.match( '^AUTOBUILD_', line ): commands.append( line )
				enabled = re.match( '^(AUTOBUILD_PACKAGE_ENABLED)\s+(\w+)$', line )
				# parse for "enabled" commands:
				try:
					if enabled:
						yesNo = str( enabled.group( 2 ) )
						if yesNo.lower() == 'false':
							packageEnabled = False
						elif yesNo.lower() == 'true':
							packageEnabled = True
						else:
							raise ConfigurationError( 'enable must be true or false' )
						mApp().debugN( self, 3, 'setBuildEnvironment: >enabled< {0}'.format( str( packageEnabled ) ) )
					else:
						if re.match( '^AUTOBUILD_', line ): commands.append( line )
				except ConfigurationError as value:
					mApp().message( 'error ({0}) in control file {1}\n--> {2}'.
						format( str( value ), controlFile, str( line ).strip() ) )
				except IndexError:
					mApp().message( 'syntax error in control file {0}\n--> {1}'.format( controlFile, str( line ).strip() ) )
			return [ packageEnabled, commands ]
		except IOError:
			mApp().debugN( self, 3, 'no control file found at "{0}"'.format( controlFile ) )
		return []

	def _controlFileName( self, path ):
		return os.path.join( path, 'AUTOBUILD_PACKAGE_CONFIGURATION' )

	def _directoryIsLeafNode( self, Folder ):
		"""find leave nodes. a leave node is a folder that contains exactly on software package,
		but no other installation nodes. software that is installed within a leaf node will not
		be found. a leaf node is discovered by the existence of the bin/ or lib/ subdirectory 
		and an  include/ subdirectory"""
		if os.path.isdir( Folder ):
			controlData = self._readControlFile( self._controlFileName( Folder ) )
			if controlData:
				[ enabled, commands ] = controlData
				if enabled:
					return True
				else:
					return False
			Elements = os.listdir( Folder )
			if ( 'bin' in Elements or 'lib' in Elements ) and ( 'include' in Elements or 'Include' in Elements or 'src' in Elements or 'boost' in Elements ):
				mApp().debugN( self, 3, '{0} is a leaf node'.format( str( Folder ) ) )
				return True
			else:
				return False

	def _findLeafNodes( self, Folder ):
		"""recursively find leaf nodes within folder"""
		LeafNodes = []
		if os.path.isdir( Folder ):
			Elements = os.listdir( Folder )
			for Element in Elements:
				mApp().debugN( self, 5, 'checking {0} for being a leaf node'.format( Element ) )
				Path = os.path.join( Folder, Element )
				if os.path.isdir( Path ):
					controlFileInfo = self._readControlFile( self._controlFileName( Path ) )
					if controlFileInfo: # there *is* a control file, and it is readable:
						if controlFileInfo[0] == False:
							# [0] is "ignore"
							mApp().debugN( self, 2, 'package directory is not enabled: "{0}"'.format( Path ) )
							continue
					if self._directoryIsLeafNode( Path ):
						LeafNodes.append( Path )
					else:
						LeafNodes = LeafNodes + self._findLeafNodes( Path )
		return LeafNodes

	def _getInstallationNodes( self, LeafNodes ):
		"""find installation nodes. an installation node is a folder that contains leaf nodes
		or other installation nodes"""
		OldCwd = os.getcwd()
		InstallationNodes = []
		for Folder in LeafNodes:
			Parts = Folder.split( os.sep )
			Parts = Parts[:-1]
			Base = os.sep.join( Parts )
			InstallationNodes.append( Base )
		# uniquify:
		UniqueInstallationNodes = []
		for Node in InstallationNodes:
			if Node not in UniqueInstallationNodes:
				UniqueInstallationNodes.append( Node )
		os.chdir( OldCwd )
		return UniqueInstallationNodes

	def _getMatchingPathList( self, EnvironmentsRoot, LeafNode, BuildDependencies, settings ):
		"""Returns a path list, looks like that: ( ( EnvPathA1, EnvPathA2, ...), (EnvPathB1, EnvPathB2, ...), ... )
		with one group (list) per dependency
		Returns None if this is no match"""
		Environments = []
		AllDependencies = list( BuildDependencies )
		OldCwd = os.getcwd()
		Folders = LeafNode.split( os.sep )
		IncrementalPaths = []
		os.chdir( EnvironmentsRoot )
		for Folder in Folders:
			if os.path.isdir( Folder ):
				os.chdir( Folder )
				IncrementalPaths.append( os.getcwd() )
		mApp().debugN( self, 4, 'incremental paths: {0}'.format( ', '.join( str( IncrementalPaths ) ) ) )
		IncrementalPaths.reverse()
		IncrementalPaths.append( '' ) # for empty paths, we check the host provided dependencies
		for Path in IncrementalPaths:
			if Path:
				os.chdir( Path )
				OriginalDependencies = list( AllDependencies ) # cannot modify AllDependencies during iteration
				for Glob in OriginalDependencies:
					mApp().debugN( self, 3, 'getMatchingPathList: checking for matches to ' + str( Glob ) + ' in ' + str( os.getcwd() ) )
					Matches = glob.glob( Glob )
					if len( Matches ) > 0:
						LeafNodeMatches = []
						for Match in Matches:
							if self._directoryIsLeafNode( Match ):
								LeafNodeMatches.append( Path + os.sep + Match )
						AllDependencies.remove( Glob )
						LeafNodeMatches.sort()
						Environments.append( LeafNodeMatches )
			else:
				# check host provided dependencies
				OriginalDependencies = list( AllDependencies ) # cannot modify AllDependencies during iteration
				for Glob in OriginalDependencies:
					mApp().debugN( self, 3, 'getMatchingPathList: checking for host provided packages matching ' + str( Glob ) )
					for ( package, path ) in settings.getHostProvidedPackages().iteritems():
						if fnmatch.fnmatch( package, Glob ):
							if self._directoryIsLeafNode( path ):
								Environments.append( [path ] )
							AllDependencies.remove( Glob )
		os.chdir( OldCwd )
		if len( AllDependencies ) == 0:
			# uniquify:
			envs = []
			for e in Environments:
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

	def findMatchingEnvironments( self ):
		# find all leaf nodes:
		BuildDependencies = None
		AutobuildEnvironmentsRoot = mApp().getSettings.get( Settings.EnvironmentsBaseDir )
		settings = None

		if os.path.isdir( AutobuildEnvironmentsRoot ):
			mApp().debugN( self, 3, 'MomEnvironments root found at "{0}"'.format( AutobuildEnvironmentsRoot ) )
			# chdir, so that all resulting leaf nodes are below AutobuildEnvironmentsRoot:
			OldCwd = os.getcwd()
			os.chdir( AutobuildEnvironmentsRoot )
			LeafNodes = self._findLeafNodes( '.' )
			mApp().debugN( self, 3, 'found leaf nodes: {0}'.format( ', '.join( str( LeafNodes ) ) ) )
			InstallationNodes = self._getInstallationNodes( LeafNodes )
			# we search an empty path as well, this makes the matcher check the host provided packages only, 
			# those could possibly fulfill all requirements as well 
			InstallationNodes.append( '' )
			mApp().debugN( self, 3, 'found installation nodes: {0}'.format( ', '.join( str( InstallationNodes ) ) ) )
			MatchingEnvironments = []
			for LeafNode in InstallationNodes:
				Match = self._getMatchingPathList( AutobuildEnvironmentsRoot, LeafNode, BuildDependencies , settings )
				if Match == None:
					mApp().debugN( self, 3, '{0} has no matching build environment for {1}'
						.format( LeafNode, str( BuildDependencies ) ) )
				else:
					mApp().debugN( self, 3, '{0} is a matching build environment for {1}'
						.format( LeafNode, str( BuildDependencies ) ) )
					MatchingEnvironments.append( Match )
			PathLists = []
			MatchingEnvironments.sort()
			for Match in MatchingEnvironments:
				self._addElementsToPathList( Match, PathLists )
			Environments = []
			for PathList in PathLists:
				Name = self._makeNameForPathList( PathList )
				Environments.append( [ Name, PathList ] )
			mApp().debugN( self, 2, 'available build environments for {0}:'.format( str( BuildDependencies ) ) )
			for Env in Environments:
				mApp().debugN( self, 2, str( Env[0] ) + ':' )
				for Path in Env[1]:
					mApp().debugN( self, 2, '--> ' + Path )
			os.chdir( OldCwd )
			return Environments
		else:
			return []
