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
from core.MObject import MObject
from core.Exceptions import AbstractMethodCalledError
from core.helpers.TypeCheckers import check_for_nonempty_string

class SourceCodeProvider( MObject ):

	def __init__( self, name ):
		"""Constructor"""
		MObject.__init__( self, name )
		self.__url = None
		self.__revision = None
		self.__committer = None
		self.__commitTime = None
		self.__commitMessage = None
		self.__srcDir = None
		self.__description = None

	def setUrl( self, url ):
		self.__url = url

	def getUrl( self ):
		return self.__url

	def setSrcDir( self, dir ):
		check_for_nonempty_string( dir, 'The course folder needs to be a non-empty string!' )
		self.__srcDir = dir

	def getSrcDir( self ):
		return self.__srcDir

	def getDescription( self ):
		return self.__description

	def _setDescription( self, description ):
		check_for_nonempty_string( description, "The SCM description needs to be a non-empty string." )
		self.__description = description

	def setRevision( self, revision ):
		self.__revision = revision

	def getRevision( self ):
		return self.__revision

	def getCommitter( self ):
		if not self.__committer:
			self._getRevisionInfo()
		return self.__committer

	def getCommitTime( self ):
		if not self.__commitTime:
			self._getRevisionInfo()
		return self.__commitTime

	def getCommitMessage( self ):
		if not self.__commitMessage:
			self._getRevisionInfo()
		return self.__commitMessage

	def _getRevisionInfo( self ):
		"""Set __committer, __commitMessage, __commitTime and __revision"""
		raise AbstractMethodCalledError

	def _checkInstallation( self, project ):
		"""Check if this SCM can be used. Should check, for example, if the SCM is actually installed."""
		raise AbstractMethodCalledError

	def makeCheckoutStep( self, project ):
		"""Create steps to check out the source code"""
		raise AbstractMethodCalledError()

	def makeExportStep( self, project, targetDir ):
		"""Create a Step that will export the source code to the target directory."""
		raise AbstractMethodCalledError()

	def makePackageStep( self, project, ):
		"""Create a src archive of the project and put it into the packages directory."""
		raise AbstractMethodCalledError()

	def preFlightCheck( self, project ):
		"""Overload"""
		self._checkInstallation( project )
		project.debug( self, 'SCM module initialized: {0}'.format( self.getDescription() ) )

	def setup( self, project ):
		"""Setup is called after the build steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makeCheckoutStep( project )
		self.makePackageStep( project )
		# FIXME it needs to be decided by the builder if this gets called!
		# self.makeExportStep( project )

	def wrapUp( self, project ):
		"""WrapUp is called when the last step has finished. It could be used to publish 
		the reports, for example."""
		pass

	def shutDown( self, project ):
		"""Shutdown is called right before the build ends. It could be used to close
		files or network connections.
		ShutDown is called from the finally block of the build method, so in all normal cases, it will be called 
		before the build script ends."""
		pass
