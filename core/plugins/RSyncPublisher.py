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
from core.Plugin import Plugin
from core.actions.ShellCommandAction import ShellCommandAction
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, check_for_path_or_none, check_for_string
import platform, os, re
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.helpers.PathResolver import PathResolver

class RSyncPublisher( Plugin ):
	'''A publisher that uses RSync to send results to a remote site.'''

	def __init__( self, name = None, uploadLocation = None, localDir = None ):
		Plugin.__init__( self, name )
		searchPaths = [ "C:/Program Files/cwRsync/bin" ]
		self._setCommand( "rsync", searchPaths )
		self.setUploadLocation( uploadLocation )
		self.setLocalDir( localDir )
		self.setStep( 'project-upload-packages' )

	def setUploadLocation( self, location ):
		check_for_nonempty_string_or_none( location, 'The rsync upload location must be a nonempty string!' )
		self.__uploadLocation = location

	def getUploadLocation( self ):
		return self.__uploadLocation

	def setLocalDir( self, localDir ):
		check_for_path_or_none( localDir, 'The local directory must be a nonempty string!' )
		self.__localDir = localDir

	def getLocalDir( self ):
		return self.__localDir

	def setStep( self, step ):
		check_for_string( step, 'The step for the rsync publisher must be a string representing a step name!' )
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
			fromDir = self.__makeCygwinPathForRsync( '{0}{1}'.format( self.getLocalDir(), os.sep ) )
			cmd = [ self.getCommand(), '-avz', '-e', 'ssh -o "BatchMode yes"', fromDir, uploadLocation ]
			action = ShellCommandAction( cmd, 7200 )
			action.setWorkingDirectory( self.getInstructions().getBaseDir() )
			step.addMainAction( action )
		else:
			mApp().debugN( self, 2, 'No local directory specified, not generating action' )


	def __makeCygwinPathForRsync( self, directory ):
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

	def describe( self, prefix, details = None, replacePatterns = True ):
		super( RSyncPublisher, self ).describe( prefix, self.getUploadLocation(), replacePatterns )

class RSyncPackagesPublisher( RSyncPublisher ):
	'''A RSync publisher that is pre-configured to publish the packages structure to the default location.'''

	def __init__( self, name = None ):
		RSyncPublisher.__init__( self, name,
			uploadLocation = mApp().getSettings().get( Settings.PublisherPackageUploadLocation ),
			localDir = PathResolver( mApp().getPackagesDir ) )
		self.setStep( 'project-upload-packages' )

# FIXME the reports publisher needs to be called after the build finished 
# (chicken and egg problem, the report can only be created once the build is done)
# implement uploading in wrapUp()?
class RSyncReportsPublisher( RSyncPublisher ):
	'''A RSync publisher that is pre-configured to publish the reports structure to the default location.'''

	def __init__( self, name = None ):
		RSyncPublisher.__init__( self, name,
			uploadLocation = mApp().getSettings().get( Settings.PublisherReportsUploadLocation ),
			localDir = PathResolver( mApp().getLogDir ) )

