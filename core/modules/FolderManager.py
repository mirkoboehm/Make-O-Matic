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
import os, time
from core.Plugin import Plugin
from core.helpers.FilesystemAccess import make_foldername_from_string
from core.Exceptions import ConfigurationError
from core.actions.filesystem.MkDirAction import MkDirAction
from core.actions.filesystem.RmDirAction import RmDirAction
from core.helpers.TypeCheckers import check_for_nonempty_string
from core.Settings import Settings
import tempfile
import shutil

class FolderManager( Plugin ):
	"""FolderManager creates and deletes the project folders."""

	def __init__( self, project ):
		Plugin.__init__( self, self.__class__.__name__ )
		self.__project = project
		self.__baseDir = None
		self._tmpLogDir = None

	def getProject( self ):
		return self.__project

	def getBaseDir( self ):
		check_for_nonempty_string( self.__baseDir, 'basedir can only be queried after preFlightCheck!' )
		return self.__baseDir

	def _setTmpLogDir( self, dir ):
		self._tmpLogDir = dir

	def getTmpLogDir( self ):
		return self._tmpLogDir

	def __getNormPath( self, name ):
		path = os.path.join( self.getBaseDir(), self.getProject().getSettings().get( name ) )
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

	def preFlightCheck( self, project ):
		buildfolderName = make_foldername_from_string( project.getName() )
		self._setTmpLogDir( tempfile.mkdtemp( '_{0}'.format( buildfolderName ), 'mom_' ) )
		project.debugN( self, 2, 'temporary log directory is at "{0}".'.format( self.getTmpLogDir() ) )
		project.getExecutomat().setLogDir( self.getTmpLogDir() )
		directory = os.path.normpath( os.getcwd() + os.sep + buildfolderName )
		project.debugN( self, 3, 'Project build folder is "{0}"'.format( directory ) )
		if os.path.isdir( directory ):
			stats = os.stat( directory )
			mtime = time.localtime( stats[8] )
			extension = time.strftime( "%Y-%m-%d-%H-%M-%S", mtime )
			newFolder = directory + '-' + extension
			try:
				os.rename( directory, newFolder )
			except OSError as o:
				raise ConfigurationError( 'Cannot move existing project build folder at "{0}" to "{1}": {2}'
										.format( directory, newFolder, str( o ) ) )
			project.debug( self, 'Project build folder exists. Existing folder moved to "{0}".'.format( newFolder ) )
		try:
			os.mkdir( directory )
		except OSError as o:
			raise ConfigurationError( 'Cannot create project build folder at "{0}": {1}'.format( directory, str( o ) ) )
		self.__baseDir = directory
		os.chdir( directory )
		project.debug( self, 'Project build folder created, current working directory is now "{0}"'.format( os.getcwd() ) )

	def setup( self, project ):
		create = project.getExecutomat().getStep( 'project-create-folders' )
		delete = project.getExecutomat().getStep( 'project-cleanup' )
		# log is never deleted
		create.addMainAction( MkDirAction( 'log' ) )
		for folder in ( self.getSourceDir(), self.getPackagesDir(), self.getTempDir() ):
			create.addMainAction( MkDirAction( folder ) )
			delete.addMainAction( RmDirAction( folder ) )

	def shutDown( self, project ):
		'''Move the temporary log dir into the base folder.'''
		try:
			# first, move a possibly existing log directory out of the way:
			if os.path.isdir( self.getLogDir() ):
				gmt = time.gmtime( os.path.getatime( self.getLogDir() ) )
				atime = time.strftime( '%Y%m%d-%H-%M-%S', gmt )
				shutil.move( self.getLogDir(), self.getLogDir() + '-' + atime )
			if self.getTmpLogDir():
				shutil.copytree( self.getTmpLogDir(), self.getLogDir() )
				shutil.rmtree( self.getTmpLogDir(), True )
				project.debugN( self, 2, 'logs moved from temporary to final location at "{0}"'.format( self.getLogDir() ) )
			self._setTmpLogDir( None )
		except ( IOError, os.error ) as why:
			project.message( 'Cannot move build logs to log directory "{0}", log data remains at "{1}": {2}'
				.format( self.getlogDir(), self.getTmpLogDir(), str( why ).strip() ) )

