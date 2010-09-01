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
from core.actions.filesystem.MkDirAction import MkDirAction
from core.actions.filesystem.RmDirAction import RmDirAction
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
import core
import os

class FolderManager( Plugin ):
	"""FolderManager creates and deletes the project folders. It is specific to Project objects."""

	def __init__( self ):
		Plugin.__init__( self )

	def getProject( self ):
		assert isinstance( self.getInstructions(), core.Project.Project )
		return self.getInstructions()

	def _setTmpLogDir( self, dir ):
		self._tmpLogDir = dir

	def getTmpLogDir( self ):
		return self._tmpLogDir

	def __getNormPath( self, name ):
		path = os.path.join( self.getInstructions().getBaseDir(), mApp().getSettings().get( name ) )
		return os.path.normpath( path )

	def getSourceDir( self ):
		return self.__getNormPath( Settings.ProjectSourceDir )

	def getPackagesDir( self ):
		return self.__getNormPath( Settings.ProjectPackagesDir )

	def getTempDir( self ):
		return self.__getNormPath( Settings.ProjectTempDir )

	def getDocsDir( self ):
		return self.__getNormPath( Settings.ProjectDocsDir )

	def getLogDir( self ):
		return self.__getNormPath( Settings.ProjectLogDir )

	def setup( self ):
		mApp().debugN( self, 3, 'build folder is "{0}"'.format( self.getInstructions().getBaseDir() ) )
		project = self.getInstructions()
		assert isinstance( project, core.Project.Project )
#		self._setTmpLogDir( tempfile.mkdtemp( '_{0}'.format( make_foldername_from_string( project.getName() ) ), 'mom_' ) )
#		mApp().debugN( self, 2, 'temporary log directory is at "{0}".'.format( self.getTmpLogDir() ) )
#		project.getExecutomat().setLogDir( self.getTmpLogDir() )
#		if os.path.isdir( project.getBaseDir() ):
#			stats = os.stat( project.getBaseDir() )
#			mtime = time.localtime( stats[8] )
#			extension = time.strftime( "%Y-%m-%d-%H-%M-%S", mtime )
#			newFolder = '{0}-{1}'.format( project.getBaseDir(), extension )
#			try:
#				shutil.move( project.getBaseDir(), newFolder )
#			except ( OSError, shutil.Error ) as o:
#				raise ConfigurationError( 'Cannot move existing build folder at "{0}" to "{1}": {2}'
#										.format( project.getBaseDir(), newFolder, str( o ) ) )
#			mApp().debug( self, 'stale build folder exists, moving it.' )
#			mApp().debugN( self, 2, 'moved to "{0}".'.format( newFolder ) )
#		try:
#			os.mkdir( project.getBaseDir() )
#		except OSError as o:
#			raise ConfigurationError( 'Cannot create project build folder at "{0}": {1}'.format( project.getBaseDir(), str( o ) ) )
#		os.chdir( project.getBaseDir() )
#		mApp().debug( self, 'build folder created' )
#		mApp().debugN( self, 2, 'CWD: "{0}"'.format( os.getcwd() ) )
		# now create actions:
		create = project.getExecutomat().getStep( 'project-create-folders' )
		delete = project.getExecutomat().getStep( 'project-cleanup' )
		for folder in ( self.getSourceDir(), self.getPackagesDir(), self.getTempDir() ):
			create.addMainAction( MkDirAction( folder ) )
			delete.addMainAction( RmDirAction( folder ) )

	def shutDown( self ):
		'''Move the temporary log dir into the base folder.'''
		pass
#		try:
#			# first, move a possibly existing log directory out of the way:
#			if os.path.isdir( self.getLogDir() ):
#				gmt = time.gmtime( os.path.getatime( self.getLogDir() ) )
#				atime = time.strftime( '%Y%m%d-%H-%M-%S', gmt )
#				shutil.move( self.getLogDir(), self.getLogDir() + '-' + atime )
#			if self.getTmpLogDir():
#				shutil.copytree( self.getTmpLogDir(), self.getLogDir() )
#				shutil.rmtree( self.getTmpLogDir(), True )
#				mApp().debugN( self, 2, 'logs moved from temporary to final location at "{0}"'.format( self.getLogDir() ) )
#			self._setTmpLogDir( None )
#		except ( IOError, os.error ) as why:
#			mApp().message( 'Cannot move build logs to log directory "{0}", log data remains at "{1}": {2}'
#				.format( self.getLogDir(), self.getTmpLogDir(), str( why ).strip() ) )

