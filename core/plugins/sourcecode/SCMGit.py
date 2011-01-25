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

from core.plugins.sourcecode.SourceCodeProvider import SourceCodeProvider
from core.Exceptions import ConfigurationError, MomError
from core.helpers.RunCommand import RunCommand
from core.actions.ShellCommandAction import ShellCommandAction
from core.actions.Action import Action
import os, sys
from core.helpers.FilesystemAccess import make_foldername_from_string
import re
from core.helpers.GlobalMApp import mApp
from core.plugins.sourcecode.RevisionInfo import RevisionInfo
from core.Settings import Settings
from buildcontrol.common.BuildInfo import BuildInfo

class _UpdateHiddenCloneAction( Action ):

	def __init__( self, scmgit ):
		Action.__init__( self )

		assert scmgit
		self.__scmgit = scmgit

	def run( self ):
		self.__scmgit.updateHiddenClone()
		return 0

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return self.getName()

class SCMGit( SourceCodeProvider ):
	"""Git SCM Provider Class"""

	def __init__( self, name = None ):
		SourceCodeProvider.__init__( self, name )
		searchPaths = []
		if sys.platform == "win32":
			from core.helpers.RegistryHelper import getPathsFromRegistry
			keys = [ "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Git_is1\\Inno Setup: App Path" ]
			searchPaths += getPathsFromRegistry( keys, "bin" )
		self._setCommand( "git" )
		self._setCommandSearchPaths( searchPaths )
		self.__cloneArmy = self._findCloneArmyDir()
		self.__cachedCheckoutsDir = self._findCachedCheckoutsDir()
		self.__revisionInfo = RevisionInfo()

	def getIdentifier( self ):
		return 'git'

	def _getCachesDir( self ):
		directory = None
		if sys.platform == 'darwin':
			directory = os.path.expanduser( "~/Library/Caches/Make-O-Matic" )
		elif sys.platform == 'win32':
			directory = os.getenv( 'LOCALAPPDATA' ) or os.getenv( 'APPDATA' )
			directory = os.path.join( directory, "Make-O-Matic", 'caches' )
		else:
			directory = os.path.expanduser( "~/.mom/caches" )
		return directory

	def _findCloneArmyDir( self ):
		name = 'clonearmy'
		if sys.platform == 'darwin':
			name = 'CloneArmy'
		path = os.path.join( self._getCachesDir(), name )
		return path

	def _findCachedCheckoutsDir( self ):
		name = 'checkouts'
		path = os.path.join( self._getCachesDir(), name )
		return path

	def getCloneArmyDir( self ):
		return self.__cloneArmy

	def getCachedCheckoutsDir( self ):
		return self.__cachedCheckoutsDir

	def getRevisionInfo( self ):
		self.updateHiddenClone()
		sep = chr( 0x0A ) + chr( 0x03 ) # use some ASCII codes as separator, to avoid clashes in commit messages
		formatStr = "%cn{0}%ce{0}%s\n\n%b{0}%ct{0}%ci{0}%H{0}%h".format( sep )

		cmd = [ self.getCommand(), 'log', '--pretty=format:{0}'.format( formatStr ), '{0}^..{0}'.format( self.getTreeish() )]
		runner = RunCommand( cmd, 3600, searchPaths = self.getCommandSearchPaths() )
		runner.setWorkingDir( self._getHiddenClonePath() )
		runner.run()

		info = RevisionInfo( "GitRevisionInfo" )

		if runner.getReturnCode() == 0:
			infos = runner.getStdOut().decode( "utf-8" ).split( sep )
			info.committerName = infos[0]
			info.committerEmail = infos[1]
			info.commitMessage = infos[2].rstrip()
			info.commitTime = infos[3]
			info.commitTimeReadable = infos[4]
			info.revision = infos[5]
			info.shortRevision = infos[6]

		return info

	def _getRevisionsSince( self, revision, cap = None ):
		"""Print revisions committed since the specified revision."""
		self.updateHiddenClone()
		cmd = [ self.getCommand(), 'log', '{0}..'.format( revision ) ]
		runner = RunCommand( cmd, 3600, searchPaths = self.getCommandSearchPaths() )
		runner.setWorkingDir( self._getHiddenClonePath() )
		runner.run()

		if runner.getReturnCode() == 0:
			revisions = []
			lines = runner.getStdOut().decode().splitlines()
			for line in lines:
				if re.match( '^commit.+', line ):
					parts = line.split( ' ' )
					hash = parts[1].strip()
					if hash == revision:
						break
					else:
						info = BuildInfo()
						info.setBuildType( 'C' ) # the default, FIXME add classifiers
						info.setRevision( hash )
						info.setUrl( self.getUrl() )
						# FIXME only master is supported this way
						info.setBranch( None )
						info.setProjectName( mApp().getSettings().get( Settings.ScriptBuildName ) )
						info.setTag( None )
						revisions.append( info )
			if cap:
				return revisions[-cap:]
			else:
				return revisions
		elif runner.getTimedOut() == True:
			raise ConfigurationError( 'Getting git log for "{0}" timed out.'.format( self.getUrl() ) )
		else:
			raise ConfigurationError( 'Getting git log failed, is there no git in the path?' )

	def _getCurrentRevision( self ):
		'''Return the identifier of the current revisions.'''
		self.updateHiddenClone()
		runner = RunCommand( [ self.getCommand(), 'log', '-n1' ], searchPaths = self.getCommandSearchPaths() )
		runner.setWorkingDir( self._getHiddenClonePath() )
		runner.run()

		if runner.getReturnCode() == 0:
			parts = runner.getStdOut().decode().splitlines()[0].strip().split()
			assert len( parts ) == 2 and parts[0] == 'commit'
			return parts[1]
		else:
			raise ConfigurationError( 'Cannot get log for the clone of "{0}" at "{1}"'
				.format( self.getUrl(), self._getHiddenClonePath() ) )

	def makeCheckoutStep( self ):
		"""Create steps to check out the source code"""

		assert self.getInstructions()
		step = self.getInstructions().getStep( 'checkout' )
		updateHiddenCloneAction = _UpdateHiddenCloneAction( self )
		step.addMainAction( updateHiddenCloneAction )

		updateCommand = [ self.getCommand(), 'clone', '--local', '--depth', '1', self._getHiddenClonePath(), "." ]
		# fix 'failed to create link' errors on windows, seems like windows does not like cross-device (hard) links 
		if sys.platform == 'win32':
			updateCommand.append( '--no-hardlinks' )
		updateClone = ShellCommandAction( updateCommand, searchPaths = self.getCommandSearchPaths() )
		updateClone.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( updateClone )

		checkoutCommand = [ self.getCommand(), 'checkout', self.getTreeish() ]
		checkout = ShellCommandAction( checkoutCommand, searchPaths = self.getCommandSearchPaths() )
		checkout.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( checkout )

	def getTreeish( self, remote = None ):
		# TODO Work out sensible ordering here or fail if we have more than one of these parameters
		treeish = self.getRevision()
		if treeish:
			return treeish

		treeish = self.getTag() or self.getBranch() or 'HEAD'
		if remote:
			treeish = '{0}/{1}'.format( remote, treeish )
		return treeish

	def __getTempRepoName( self ):
		tempName = make_foldername_from_string( self.getUrl() )
		return tempName

	def _getHiddenClonePath( self ):
		hiddenClone = os.path.join( self.getCloneArmyDir(), self.__getTempRepoName() )
		return hiddenClone

	def _getCachedCheckoutPath( self ):
		cachedCheckout = os.path.join( self.getCachedCheckoutsDir(), self.__getTempRepoName() )
		return cachedCheckout

	def updateHiddenClone( self ):
		hiddenClone = self._getHiddenClonePath()
		# check if the clone directory exists, create if necessary: 
		if os.path.exists( hiddenClone ):
			if not os.path.isdir( hiddenClone ):
				raise MomError( 'hidden clone exists at "{0}", but is not a directory. Help!'.format( hiddenClone ) )
			# FIXME get timeout value from settings
			fetchCommand = [ self.getCommand(), 'fetch', '--all' ]
			runner = RunCommand( fetchCommand, 1200, True, searchPaths = self.getCommandSearchPaths() )
			runner.setWorkingDir( hiddenClone )
			runner.run()
			if runner.getReturnCode() == 0:
				mApp().debugN( self, 4, 'updated the hidden clone at "{0}"'.format( hiddenClone ) )
			else:
				raise MomError( 'cannot update the clone of "{0}" at "{1}"'.format( self.getUrl(), hiddenClone ) )
		else:
			if not os.path.exists( self.getCloneArmyDir() ):
				os.makedirs( self.getCloneArmyDir() )
			cloneCommand = [ self.getCommand(), 'clone', '--mirror', self.getUrl(), make_foldername_from_string( self.getUrl() ) ]
			runner = RunCommand( cloneCommand, 1200, True, searchPaths = self.getCommandSearchPaths() )
			runner.setWorkingDir( self.getCloneArmyDir() )
			runner.run()

			if runner.getReturnCode() == 0:
				mApp().debugN( self, 2, 'Created a hidden clone at "{0}"'.format( hiddenClone ) )
			else:
				if runner.getStdOut().find( "unknown option `mirror'" ):
					raise ConfigurationError( 'Please install newer version of Git that supports the "--mirror" option' )
				raise MomError( 'cannot create clone of "{0}" at "{1}"'.format( self.getUrl(), hiddenClone ) )

	def updateCachedCheckout( self ):
		treeish = self.getTreeish( 'origin' )
		if not os.path.exists( self.getCachedCheckoutsDir() ):
			try:
				os.makedirs( self.getCachedCheckoutsDir() )
			except ( IOError, OSError ) as e:
				raise MomError( 'Error creating cached checkouts dir at {0}: {1}'.format( 
					self.getCachedCheckoutsDir(), e ) )
		if os.path.exists( self._getCachedCheckoutPath() ):
			# update an existing repository
			mApp().debugN( self, 3, 'updating the cached checkout at "{0}" to treeish {1}'.format( 
				self.getCachedCheckoutsDir(), treeish ) )
			# reset the hidden clone to a branch
			resetRunner = RunCommand( [ self.getCommand(), 'fetch', '--all' ], searchPaths = self.getCommandSearchPaths() )
			resetRunner.setWorkingDir( self._getCachedCheckoutPath() )
			resetRunner.run()
			if resetRunner.getReturnCode() != 0:
				raise MomError( 'error fetching revisions into the hidden clone' )
			# FIXME we may not be on the master branch:
		else:
			mApp().debugN( self, 2, 'creating the cached checkout at "{0}" with treeish {1}'.format( 
				self.getCachedCheckoutsDir(), treeish ) )
			# create the clone
			cloneCmd = [ self.getCommand(), 'clone', self._getHiddenClonePath(), self.__getTempRepoName() ]
			cloneRunner = RunCommand( cloneCmd, searchPaths = self.getCommandSearchPaths() )
			cloneRunner.setWorkingDir( self.getCachedCheckoutsDir() )
			cloneRunner.run()
			if cloneRunner.getReturnCode() != 0:
				raise ConfigurationError( 'Cannot create the cached checkout at {0}'.format( 
					self.getCachedCheckoutsDir() ) )
		# now checkout the requested treeish
		checkoutCmd = [ self.getCommand(), 'checkout', treeish ]
		checkoutRunner = RunCommand( checkoutCmd, searchPaths = self.getCommandSearchPaths() )
		checkoutRunner.setWorkingDir( self._getCachedCheckoutPath() )
		checkoutRunner.run()
		if checkoutRunner.getReturnCode() != 0:
			# FIXME delete, continue with regular checkout
			raise ConfigurationError( 'Cannot update the checkout at {0} to treeish {1}'.format( 
				self.getCachedCheckoutsDir(), treeish ) )

	def fetchRepositoryFolder( self, remotePath ):
		self.updateHiddenClone()
		self.updateCachedCheckout()
		hiddenCheckoutPath = os.path.join( self._getCachedCheckoutPath(), remotePath )
		if os.path.exists( hiddenCheckoutPath ):
			return hiddenCheckoutPath
		else:
			raise ConfigurationError( 'The remote path {0} was not found in the repository at treeish {1}'.format( 
					remotePath, self.getTreeish() ) )
