# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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
import platform, os, re, tempfile
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.helpers.PathResolver import PathResolver
from core.actions.Action import Action
from core.helpers.RunCommand import RunCommand
from core.plugins.publishers.Publisher import Publisher

class _CreateUploadDirectoryAction( Action ):
	def __init__( self, publisher ):
		Action.__init__( self )
		self.__publisher = publisher

	def getLogDescription( self ):
		return 'Create rsync upload target path if extra subdirectories are specified.'

	def run( self ):
		if self.__publisher.getExtraUploadSubDirs():
			path = os.path.join( *self.__publisher._getExtraUploadSubdirsAsString() )
			tempDir = tempfile.mkdtemp( prefix = 'mom_buildscript-', suffix = '-rsync-path' )
			fullpath = os.path.join( tempDir, path )
			os.makedirs( fullpath )
			uploadLocation = self.__publisher._getUploadLocationOrDefault()
			args = [ '-avz', '-e', 'ssh -o BatchMode=yes', tempDir + os.sep, uploadLocation ]
			cmd = [ self.__publisher.getCommand() ] + args
			runner = RunCommand( cmd, timeoutSeconds = 1200, searchPaths = self.__publisher.getCommandSearchPaths() )
			if runner.run() != 0:
				mApp().debugN( self, 1, 'Creating extra sub directories {0} on the upload server failed!'.format( path ) )
				return runner.getReturnCode()
			else:
				mApp().debugN( self, 3, 'Created extra sub directories {0} on the upload server.'.format( path ) )
				return 0

class _RSyncUploadAction( Action ):
	'''RSyncUploadAction uses RSync to publish data from the local directory to the upload location.
	It determines the local and target location at execution time.'''
	def __init__( self, publisher ):
		Action.__init__( self )
		self.__publisher = publisher

	def getLogDescription( self ):
		return 'Upload files to "{0}"'.format( self.__publisher._getUploadLocationOrDefault() )

	def run( self ):
		fromDir = self.__publisher._makeCygwinPathForRsync( '{0}{1}'.format( self.__publisher.getLocalDir(), os.sep ) )
		toDir = os.path.join( self.__publisher._getUploadLocationOrDefault(), *self.__publisher._getExtraUploadSubdirsAsString() )
		args = [ '-avz', '-e', 'ssh -o BatchMode=yes', fromDir, toDir ]
		if 'Windows' in platform.platform(): #On windows, fake source permissions to be 755
			args = [ '--chmod=ugo=rwx' ] + args
		cmd = [ self.__publisher.getCommand() ] + args
		runner = RunCommand( cmd, timeoutSeconds = 7200, searchPaths = self.__publisher.getCommandSearchPaths() )
		if runner.run() != 0:
			mApp().debugN( self, 1, 'Uploading from "{0}" to "{1}" failed!'.format( fromDir, toDir ) )
			return runner.getReturnCode()
		else:
			mApp().debugN( self, 3, 'Uploaded "{0}" to "{1}".'.format( fromDir, toDir ) )
			return 0


class RSyncPublisher( Publisher ):
	'''A publisher that uses RSync to send results to a remote site.'''

	def __init__( self, name = None, uploadLocation = None, localDir = None ):
		Publisher.__init__( self, name )
		searchPaths = [ "C:/Program Files/cwRsync/bin" ]
		self._setCommand( "rsync" )
		self._setCommandSearchPaths( searchPaths )
		self.setUploadLocation( uploadLocation )
		self.setLocalDir( localDir )
		self.setStep( 'upload-packages' )

	def _getUploadLocationOrDefault( self ):
		uploadLocation = self.getUploadLocation()
		if not uploadLocation:
			defaultLocation = mApp().getSettings().get( Settings.RSyncPublisherPackageUploadLocation, False )
			mApp().debugN( self, 3, 'Upload location not specified, using default "{0}".'.format( defaultLocation ) )
			uploadLocation = defaultLocation
		return uploadLocation

	def setup( self ):
		uploadLocation = self._getUploadLocationOrDefault()
		if not uploadLocation:
			mApp().message( self, 'Upload location is empty. Not generating any actions.' )
			return
		step = self.getInstructions().getStep( self.getStep() )
		if str( self.getLocalDir() ):
			subdirsAction = _CreateUploadDirectoryAction( self )
			step.addMainAction( subdirsAction )
			uploadAction = _RSyncUploadAction( self )
			step.addMainAction( uploadAction )
		else:
			mApp().debugN( self, 2, 'No local directory specified, not generating action' )

	def _makeCygwinPathForRsync( self, directory ):
		"""This function generates a path understood by Cygwin from a Windows  
		path that contains a drive letter. Rsync otherwise interprets the letter 
		before the colon as a target hostname. On all other platforms, this function does nothing."""
		# be transparent on non-Windows platforms: 
		if not directory or not 'Windows' in platform.platform():
			return directory
		# normalize the path 
		hasEndingSlash = directory.strip()[-1] == '\\'
		directory = os.path.normpath( directory )
		if hasEndingSlash: # normpath strips trailing slashes  
			directory += '/' # *now* we ar on Unix, sigh :-)  
		# remove leading whitespace, to be sure 
		directory = re.sub( '^\s+', '', directory )
		assert directory
		# if we are on Windows and the path starts with a drive letter: 
		if re.match( '^\s*[a-zA-Z]\:', directory ):
			driveLetter = directory[0]
			directory = directory[2:]
		# we *do* *require* cygwin rsync on Windows!
		directory = '/cygdrive/' + driveLetter + directory
		directory = re.sub( '\\\\+', '/', directory )
		return directory

class RSyncPackagesPublisher( RSyncPublisher ):
	'''A RSync publisher that is pre-configured to publish the packages structure to the default location.'''

	def __init__( self, name = None ):
		RSyncPublisher.__init__( self, name,
			uploadLocation = mApp().getSettings().get( Settings.RSyncPublisherPackageUploadLocation ),
			localDir = PathResolver( mApp().getPackagesDir ) )
		self.setStep( 'upload-packages' )

	def getObjectStatus( self ):
		baseUrl = mApp().getSettings().get( Settings.PublisherPackageBaseHttpURL, False )
		if baseUrl:
			return "Location: {0}".format( baseUrl )

		super( RSyncPackagesPublisher, self ).getObjectStatus()

# FIXME the reports publisher needs to be called after the build finished 
# (chicken and egg problem, the report can only be created once the build is done)
# implement uploading in wrapUp()?
class RSyncReportsPublisher( RSyncPublisher ):
	'''A RSync publisher that is pre-configured to publish the reports structure to the default location.'''

	def __init__( self, name = None ):
		RSyncPublisher.__init__( self, name,
			uploadLocation = mApp().getSettings().get( Settings.RSyncPublisherReportsUploadLocation ),
			localDir = PathResolver( mApp().getLogDir ) )

	def getObjectStatus( self ):
		baseUrl = mApp().getSettings().get( Settings.PublisherReportsBaseHttpURL, False )
		if baseUrl:
			return "Location: {0}".format( baseUrl )

		super( RSyncReportsPublisher, self ).getObjectStatus()
