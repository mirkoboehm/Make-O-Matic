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
from core.Plugin import Plugin
from core.helpers.RunCommand import RunCommand
from core.Exceptions import ConfigurationError
from core.executomat.ShellCommandAction import ShellCommandAction
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, check_for_path_or_none
import platform, os, re
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp

class RSyncPublisher( Plugin ):
	'''A publisher that uses RSync to send results to a remote site.'''

	def __init__( self, name = None, uploadLocation = None, localDir = None ):
		"""Constructor"""
		Plugin.__init__( self, name )
		self.setUploadLocation( uploadLocation )
		self.setLocalDir( localDir )

	def setUploadLocation( self, location ):
		check_for_nonempty_string_or_none( location, 'The rsync upload location must be a nonempty string!' )
		self.__uploadLocation = location

	def getUploadLocation( self ):
		return self.__uploadLocation

	def setLocalDir( self, dir ):
		check_for_path_or_none( dir, 'The local directory must be a nonempty string!' )
		self.__localDir = dir

	def getLocalDir( self ):
		return self.__localDir

	def preFlightCheck( self ):
		runner = RunCommand( 'rsync --version' )
		runner.run()
		if( runner.getReturnCode() != 0 ):
			raise ConfigurationError( "RSyncPublisher: rsync not found." )
		else:
			lines = runner.getStdOut().decode().split( '\n' )
			version = lines[0].rstrip()
			mApp().debugN( self, 1, 'rsync found: "{0}"'.format( version ) )

	def setup( self ):
		uploadLocation = self.getUploadLocation()
		if not uploadLocation:
			defaultLocation = mApp().getSettings().get( Settings.RSyncPublisherUploadLocation, False )
			mApp().debugN( self, 3, 'Upload location not specified, using default "{0}".'.format( defaultLocation ) )
			uploadLocation = defaultLocation
			if not uploadLocation:
				mApp().message( self, 'Upload location is empty. Not generating any actions.' )
				return
		step = self.getInstructions().getExecutomat().getStep( 'project-upload-docs' )
		fromDir = self.__makeCygwinPathForRsync( '{0}{1}'.format( self.getLocalDir(), os.sep ) )
		action = ShellCommandAction( 'rsync -avz -e \'ssh -o "BatchMode yes"\' {0} {1}'.format( fromDir, uploadLocation ), 7200 )
		action.setWorkingDirectory( self.getInstructions().getBaseDir() )
		step.addMainAction( action )


	def __makeCygwinPathForRsync( self, dir ):
		"""This function generates a path understood by Cygwin from a Windows  
		path that contains a drive letter. Rsync otherwise interprets the letter 
		before the colon as a target hostname. On all other platforms, this function does nothing."""
		# be transparent on non-Windows platforms: 
		if not dir or not 'Windows' in platform.platform():
			return dir
		# normalize the path 
		hasEndingSlash = dir.strip()[-1] == '\\'
		dir = os.path.normpath( dir )
		if hasEndingSlash: # normpath strips trailing slashes  
			dir += '/' # *now* we ar on Unix, sigh :-)  
		# remove leading whitespace, to be sure 
		dir = re.sub( '^\s+', '', dir )
		assert dir
		# if we are on Windows and the path starts with a drive letter: 
		if re.match( '^\s*[a-zA-Z]\:', dir ):
			driveLetter = dir[0]
			dir = dir[2:]
		# we *do* *require* cygwin rsync on Windows!
		dir = '/cygdrive/' + driveLetter + dir
		dir = re.sub( '\\\\+', '/', dir )
		return dir
