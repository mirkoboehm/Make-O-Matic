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
from core.Plugin import Plugin
from core.actions.filesystem.DirectoryTreeCopyAction import DirectoryTreeCopyAction
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, check_for_path_or_none, check_for_string
import platform, os, re
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.helpers.PathResolver import PathResolver

class FileSystemPublisher( Plugin ):
	'''A publisher that copies the files in the filesystem.'''

	def __init__( self, name = None, uploadLocation = None, localDir = None ):
		Plugin.__init__( self, name )
		self.setUploadLocation( uploadLocation )
		self.setLocalDir( localDir )
		self.setStep( 'upload-packages' )

	def getObjectStatus( self ):
		return "Upload location: {0}".format( self.getUploadLocation() )

	def setUploadLocation( self, location ):
		check_for_nonempty_string_or_none( location, 'The filesystem upload location must be a nonempty string!' )
		self.__uploadLocation = location

	def getUploadLocation( self ):
		return self.__uploadLocation

	def setLocalDir( self, localDir ):
		check_for_path_or_none( localDir, 'The local directory must be a nonempty string!' )
		self.__localDir = localDir

	def getLocalDir( self ):
		return self.__localDir

	def setStep( self, step ):
		check_for_string( step, 'The step for the filesystem publisher must be a string representing a step name!' )
		self.__step = step

	def getStep( self ):
		return self.__step

	def setup( self ):
		uploadLocation = self.getUploadLocation()
		if not uploadLocation:
			defaultLocation = mApp().getSettings().get( Settings.PublisherPackageUploadLocation, False )
			mApp().debugN( self, 3, 'Upload location not specified, using default "{0}".'.format( defaultLocation ) )
			uploadLocation = defaultLocation
			if not uploadLocation:
				mApp().message( self, 'Upload location is empty. Not generating any actions.' )
				return
		step = self.getInstructions().getStep( self.getStep() )
		if str( self.getLocalDir() ):
			action = DirectoryTreeCopyAction( str( self.getLocalDir() ), self.getUploadLocation(), overwrite = True )
			step.addMainAction( action )
		else:
			mApp().debugN( self, 2, 'No local directory specified, not generating action' )


class FileSystemPackagesPublisher( FileSystemPublisher ):
	'''A filesystem publisher that is pre-configured to publish the packages structure to the default location.'''

	def __init__( self, name = None ):
		FileSystemPublisher.__init__( self, name,
			uploadLocation = mApp().getSettings().get( Settings.PublisherPackageUploadLocation ),
			localDir = PathResolver( mApp().getPackagesDir ) )
		self.setStep( 'upload-packages' )

	def getObjectStatus( self ):
		baseUrl = mApp().getSettings().get( Settings.PublisherPackageBaseHttpURL, False )
		if baseUrl:
			return "Location: {0}".format( baseUrl )

		super( FileSystemPackagesPublisher, self ).getObjectStatus()

# FIXME the reports publisher needs to be called after the build finished 
# (chicken and egg problem, the report can only be created once the build is done)
# implement uploading in wrapUp()?
class FileSystemReportsPublisher( FileSystemPublisher ):
	'''A filesystem publisher that is pre-configured to publish the reports structure to the default location.'''

	def __init__( self, name = None ):
		FileSystemPublisher.__init__( self, name,
			uploadLocation = mApp().getSettings().get( Settings.PublisherReportsUploadLocation ),
			localDir = PathResolver( mApp().getLogDir ) )

	def getObjectStatus( self ):
		baseUrl = mApp().getSettings().get( Settings.PublisherReportsBaseHttpURL, False )
		if baseUrl:
			return "Location: {0}".format( baseUrl )

		super( FileSystemReportsPublisher, self ).getObjectStatus()