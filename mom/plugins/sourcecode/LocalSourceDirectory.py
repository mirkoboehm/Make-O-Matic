# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko.boehm@kdab.com>
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
from core.helpers.RevisionInfo import RevisionInfo
from core.Exceptions import ConfigurationError, MomError
import os, getpass

class LocalSourceDirectory( SourceCodeProvider ):
	'''LocalSourceDirectory uses a directory on the file system to provide the source code for the build.'''

	def __init__( self, name = None ):
		SourceCodeProvider.__init__( self, name )

	def getIdentifier( self ):
		return 'src'

	def _retrieveRevisionInfo( self ):
		# check if specified revision is in cache. do not check for 'HEAD'
		info = RevisionInfo( "LocalSourceDirRevisionInfo" )
		info.commitMessage = 'N/A'
		info.committerEmail = 'N/A'
		info.committerName = getpass.getuser()
		info.commitTime = 0
		info.commitTimeReadable = 'N/A'
		info.revision = 'N/A'
		return info

	def _getRevisionsSince( self, revision, cap = None ):
		return []

	def _getCurrentRevision( self ):
		return 'N/A'

	def makeCheckoutStep( self ):
		folder = self.getUrl()
		if not os.path.isdir( folder ):
			raise ConfigurationError( 'The local source directory "{0}" does not exist!'.format( folder ) )
		project = self.getInstructions()
		project.setSourceDir( os.path.abspath( folder ) )

	def fetchRepositoryFolder( self, remotePath ):
		raise MomError( 'Remote building cannot be used with a local source directory!' )
