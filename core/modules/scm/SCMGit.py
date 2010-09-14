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
from core.modules.SourceCodeProvider import SourceCodeProvider
from core.Exceptions import ConfigurationError, MomError
from core.helpers.RunCommand import RunCommand
from core.executomat.ShellCommandAction import ShellCommandAction
from core.executomat.Action import Action
import os, sys
from core.helpers.FilesystemAccess import make_foldername_from_string
import re
from core.helpers.GlobalMApp import mApp

class _UpdateHiddenCloneAction( Action ):
	def __init__( self, scmgit ):
		Action.__init__( self )
		assert scmgit
		self.__scmgit = scmgit

	def run( self ):
		self.__scmgit._updateHiddenClone()
		return 0

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return self.getName()

class SCMGit( SourceCodeProvider ):
	"""Git SCM Provider Class"""

	def __init__( self, name = None ):
		SourceCodeProvider.__init__( self, name )
		if sys.platform == 'darwin':
			self.__cloneArmy = os.path.expanduser( "~/Library/Caches/MakeOMatic/CloneArmy" )
		elif sys.platform == 'win32':
			self.__cloneArmy = os.getenv( 'LOCALAPPDATA' ) or os.getenv( 'APPDATA' )
			self.__cloneArmy = os.path.join( self.__cloneArmy, "MakeOMatic" )
		else:
			self.__cloneArmy = os.path.expanduser( "~/.cloneArmy" )
		self._setCommand( "git" )

	def getIdentifier( self ):
		return 'git'

	def getCloneArmyDir( self ):
		return self.__cloneArmy

	def _getRevisionInfo( self ):
		"""Set __committer, __commitMessage, __commitTime and __revision"""
		raise NotImplementedError

	def _getRevisionsSince( self, revision, cap = None ):
		"""Print revisions committed since the specified revision."""
		self._updateHiddenClone()
		cmd = [ self.getCommand(), 'log', '{0}..'.format( revision ) ]
		runner = RunCommand( cmd, 3600 )
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
						data = ( 'C', hash, self.getUrl() )
						revisions.append( data )
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
		self._updateHiddenClone()
		runner = RunCommand( [ self.getCommand(), 'log', '-n1' ] )
		runner.setWorkingDir( self._getHiddenClonePath() )
		runner.run()

		if runner.getReturnCode() == 0:
			parts = runner.getStdOut().decode().splitlines()[0].strip().split()
			assert len( parts ) == 2 and parts[0] == 'commit'
			return parts[1]
		else:
			raise ConfigurationError( 'cannot get log for the clone of "{0}" at "{1}"'
				.format( self.getUrl(), self._getHiddenClonePath() ) )

	def makeCheckoutStep( self ):
		"""Create steps to check out the source code"""
		assert self.getInstructions()
		step = self.getInstructions().getStep( 'project-checkout' )
		updateHiddenCloneAction = _UpdateHiddenCloneAction( self )
		step.addMainAction( updateHiddenCloneAction )
		updateClone = ShellCommandAction( [ self.getCommand(), 'clone', '--local', '--depth', '1', self._getHiddenClonePath(), "." ] )
		updateClone.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( updateClone )
		revision = self.getRevision() or 'HEAD'
		checkout = ShellCommandAction( [ self.getCommand(), 'checkout', revision ] )
		checkout.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( checkout )

	def _getHiddenClonePath( self ):
		clonename = make_foldername_from_string( self.getUrl() )
		hiddenClone = os.path.join( self.getCloneArmyDir(), clonename )
		return hiddenClone

	def _updateHiddenClone( self ):
		hiddenClone = self._getHiddenClonePath()
		# check if the clone directory exists, create if necessary: 
		if os.path.exists( hiddenClone ):
			if not os.path.isdir( hiddenClone ):
				raise MomError( 'hidden clone exists at "{0}", but is not a directory. Help!'.format( hiddenClone ) )
			# FIXME get timeout value from settings
			runner = RunCommand( [ self.getCommand(), 'fetch', '--all' ], 1200, True )
			runner.setWorkingDir( hiddenClone )
			runner.run()
			if runner.getReturnCode() == 0:
				mApp().debugN( self, 4, 'updated the hidden clone at "{0}"'.format( hiddenClone ) )
			else:
				raise MomError( 'cannot update the clone of "{0}" at "{1}"'.format( self.getUrl(), hiddenClone ) )
		else:
			if not os.path.exists( self.getCloneArmyDir() ):
				os.makedirs( self.getCloneArmyDir() )
			runner = RunCommand( [ self.getCommand(), 'clone', '--bare', self.getUrl(), make_foldername_from_string( self.getUrl() ) ], 1200, True )
			runner.setWorkingDir( self.getCloneArmyDir() )
			runner.run()
			if runner.getReturnCode() == 0:
				mApp().debugN( self, 2, 'Created a hidden clone at "{0}"'.format( hiddenClone ) )
			else:
				raise MomError( 'cannot create clone of "{0}" at "{1}"'.format( self.getUrl(), hiddenClone ) )

