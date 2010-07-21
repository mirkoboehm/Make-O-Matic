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

class FolderManager( Plugin ):
	"""FolderManager creates and deletes the project folders."""

	def __init__( self ):
		Plugin.__init__( self, self.__class__.__name__ )
		self.__baseDir = None

	def getBaseDir( self ):
		check_for_nonempty_string( self.__baseDir, 'basedir can only be queried after preFlightCheck!' )
		return self.__baseDir

	def __getNormPath( self, project, name ):
		path = os.path.join( self.getBaseDir(), project.getSettings().get( name ) )
		return os.path.normpath( path )

	def getSourceDir( self, project ):
		return self.__getNormPath( project, Settings.ProjectSourceDir )

	def getPackagesDir( self, project ):
		return self.__getNormPath( project, Settings.ProjectPackagesDir )

	def getTempDir( self, project ):
		return self.__getNormPath( project, Settings.ProjectTempDir )

	def getDocsDir( self, project ):
		return self.__getNormPath( project, Settings.ProjectDocsDir )

	def preFlightCheck( self, project ):
		buildfolderName = make_foldername_from_string( project.getName() )
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
		for folder in ( self.getSourceDir( project ), self.getPackagesDir( project ), self.getTempDir( project ) ):
			create.addMainAction( MkDirAction( folder ) )
			delete.addMainAction( RmDirAction( folder ) )

