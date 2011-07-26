# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Andreas Holzammer <andy@kdab.com>
#
# Make-O-Matic is free software: you can redistribute it and/or modify
# it un>r the terms of the GNU General Public License as published by
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

from core.plugins.publishers.Publisher import Publisher
from core.actions.filesystem.DirectoryTreeCopyAction import DirectoryTreeCopyAction
from core.actions.filesystem.CheckDirectoryExistsAction import CheckDirectoryExistsAction
from core.helpers.GlobalMApp import mApp
from core.helpers.PathResolver import PathResolver
import os

class FileSystemPublisher( Publisher ):
	'''A publisher that copies the files in the file system.'''

	def __init__( self, name = None, uploadLocation = None, localDir = None ):
		Publisher.__init__( self, name )
		self.setUploadLocation( uploadLocation )
		self.setLocalDir( localDir )
		self._setStep( 'upload-packages' )

	def setup( self ):
		if not self.getUploadLocation():
			mApp().message( self, 'Upload location is empty. Not generating any actions.' )
			return

		localdir = self.getLocalDir()
		if not self.getLocalDir():
			localdir = PathResolver( mApp().getPackagesDir )
		step = self.getInstructions().getStep( self.getStep() )
		if str( localdir ):
			checkaction = CheckDirectoryExistsAction( os.path.dirname( self.getUploadLocation() ) )
			step.addMainAction( checkaction )
			action = DirectoryTreeCopyAction( localdir, PathResolver( self._getFullUploadLocation ), overwrite = True )
			step.addMainAction( action )
		else:
			mApp().debugN( self, 2, 'No local directory specified, not generating action' )


class FileSystemPackagesPublisher( FileSystemPublisher ):
	'''A filesystem publisher that is pre-configured to publish the packages structure to the default location.'''

	def __init__( self, name = None ):
		FileSystemPublisher.__init__( self, name,
			localDir = PathResolver( mApp().getPackagesDir ) )
		self._setStep( 'upload-packages' )


class FileSystemReportsPublisher( FileSystemPublisher ):
	'''A filesystem publisher that is pre-configured to publish the reports structure to the default location.'''

	def __init__( self, name = None ):

		FileSystemPublisher.__init__( self, name,
			localDir = PathResolver( mApp().getLogDir ) )
