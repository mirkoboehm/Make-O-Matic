# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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
from core.MObject import MObject
import sqlite3, os, shutil
from buildcontrol.common.BuildInfo import BuildInfo
from core.Exceptions import MomError, ConfigurationError
from core.Settings import Settings
from buildcontrol.common.BuildScriptInterface import BuildScriptInterface
from core.helpers.FilesystemAccess import make_foldername_from_string
from core.helpers.GlobalMApp import mApp
from buildcontrol.SubprocessHelpers import extend_debug_prefix
from core.helpers.EnvironmentSaver import EnvironmentSaver

class BuildStatus( MObject ):
	'''Build status stores the status of each individual revision in a sqlite3 database.'''

	TableName = 'build_status'

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.setDatabaseFilename( None )

	def setDatabaseFilename( self, filePath ):
		self.__databaseFilename = filePath

	def getDatabaseFilename( self ):
		return self.__databaseFilename

	def getConnection( self ):
		conn = sqlite3.connect( self.getDatabaseFilename() )
		conn.execute( '''CREATE TABLE IF NOT EXISTS {0} (
id INTEGER PRIMARY KEY AUTOINCREMENT,
project_name text,
status int,
priority int,
type text,
revision text,
url text,
script text
)'''.format( BuildStatus.TableName ) )
		conn.commit()
		return conn

	def _saveBuildInfo( self, connection, buildInfos ):
		try:
			cursor = connection.cursor()
			for buildInfo in buildInfos:
				values = [
					buildInfo.getProjectName(),
					buildInfo.getBuildStatus(),
					buildInfo.getPriority(),
					buildInfo.getBuildType(),
					buildInfo.getRevision(),
					buildInfo.getUrl(),
					buildInfo.getBuildScript() ]
				query = '''insert into {0}
( id, project_name, status, priority, type, revision, url, script )
values ( NULL, ?, ?, ?, ?, ?, ?, ? )'''.format( BuildStatus.TableName )
				cursor.execute( query, values )
				buildInfo.setBuildId( cursor.lastrowid )
		finally:
			cursor.close()

	def saveBuildInfo( self, buildInfos ):
		with self.getConnection() as connection:
			self._saveBuildInfo( connection, buildInfos )

	def _updateBuildInfo( self, connection, buildInfo, ):
		try:
			c = connection.cursor()
			values = [
				buildInfo.getProjectName(),
				buildInfo.getBuildStatus(),
				buildInfo.getPriority(),
				buildInfo.getBuildType(),
				buildInfo.getRevision(),
				buildInfo.getUrl(),
				buildInfo.getBuildScript(),
				buildInfo.getBuildId() ]
			query = '''update {0} set project_name=?, status=?, priority=?, type=?, revision=?, url=?, script=? where id=?'''\
				.format( BuildStatus.TableName )
			c.execute( query, values )
		finally:
			c.close()

	def updateBuildInfo( self, buildInfo ):
		with self.getConnection() as conn:
			self._updateBuildInfo( conn, buildInfo )

	def __makeBuildInfoFromRow( self, row ):
		buildInfo = BuildInfo()
		buildInfo.setBuildId( row[0] )
		buildInfo.setProjectName( row[1] )
		buildInfo.setBuildStatus( row[2] )
		buildInfo.setPriority( row[3] )
		buildInfo.setBuildType( row[4] )
		buildInfo.setRevision( row[5] )
		buildInfo.setUrl( row[6] )
		buildInfo.setBuildScript( row[7] )
		return buildInfo

	def _loadBuildInfo( self, connection , status ):
		try:
			cursor = connection.cursor()
			query = 'select * from {0} where status=? order by priority desc'.format( BuildStatus.TableName )
			cursor.execute( query, [ status ] )
			buildInfos = []
			for row in cursor:
				buildInfo = self.__makeBuildInfoFromRow( row )
				buildInfos.append( buildInfo )
			return buildInfos
		finally:
			cursor.close()

	def loadBuildInfo( self, status = BuildInfo.Status.NewRevision ):
		'''Load all BuildInfo objects from the database that are in the specified status.'''
		with self.getConnection() as connection:
			return self._loadBuildInfo( connection, status )

	def registerNewRevisions( self, buildScript ):
		'''Determines new revisions committed since the last call with the same build script, 
		and adds those to the database.'''
		iface = BuildScriptInterface( buildScript )
		projectName = iface.querySetting( Settings.ProjectName )
		newestBuildInfo = self.getNewestBuildInfo( buildScript )
		if newestBuildInfo:
			revision = newestBuildInfo.getRevision()
			mApp().debugN( self, 2, 'newest known revision for build script "{0}" ({1}) is "{2}"'
				.format( buildScript, projectName, revision ) )
			buildInfos = self.getBuildInfoForRevisionsSince( buildScript, projectName, revision )
			if buildInfos:
				mApp().message( self, 'build script "{0}" ({1}):'.format( buildScript, projectName ) )
				for buildInfo in buildInfos:
					msg = 'new revision "{0}"'.format( buildInfo.getRevision() )
					mApp().message( self, msg )
				self.saveBuildInfo( buildInfos )
			else:
				mApp().debug( self, 'no new revisions found for build script "{0}" ({1})'
					.format( buildScript, projectName ) )
		else:
			buildInfo = self.getBuildInfoForInitialRevision( buildScript, projectName )
			mApp().debug( self, 'saving initial revision "{0}" for build script "{1}" ({2})'
				.format( buildInfo.getRevision(), buildScript, projectName ) )
			self.saveBuildInfo( [ buildInfo ] )

	def listNewBuildInfos( self ):
		connection = self.getConnection()
		try:
			cursor = connection.cursor()
			query = 'select * from {0} where status=? order by priority desc'.format( BuildStatus.TableName )
			cursor.execute( query, [ BuildInfo.Status.NewRevision ] )
			buildInfos = []
			for row in cursor:
				buildInfo = self.__makeBuildInfoFromRow( row )
				buildInfos.append( buildInfo )
			if buildInfos:
				mApp().debug( self, 'build queue:' )
				for buildInfo in buildInfos:
					mApp().debug( self, '{0} {1}: {2} - {3}'.format( 
						buildInfo.getBuildType().upper() or ' ',
						buildInfo.getProjectName(),
						buildInfo.getRevision(),
						buildInfo.getUrl() ) )
			else:
				mApp().debug( self, 'build queue is empty.' )
			return buildInfos
		finally:
			cursor.close()

	def performBuild( self, buildInfo ):
		"""Start a build process for a new revision. baseDir is the directory where all builds go. To build 
		different revisions and build types under it, subdirectories have to be used."""
		buildType = buildInfo.getBuildType().lower()
		rev = buildInfo.getRevision()
		name = make_foldername_from_string( buildInfo.getProjectName() )
		# find suitable names for the different build dirs:
		# <build type>/<project, branch or tag name>-revision/
		# FIXME get baseDir from settings
		baseDir = 'builds'
		subfolder = make_foldername_from_string( rev )
		directory = os.path.normpath( os.path.join( os.getcwd(), baseDir, buildType, name, subfolder ) )
		# prepare build directory:
		if os.path.isdir( directory ):
			mApp().debug( self, 'found remainders of a previous build, nuking it...' )
			try:
				shutil.rmtree( directory )
				mApp().debug( self, '...that was good!' )
			except ( OSError, IOError ) as e:
				raise ConfigurationError( 'Remnants of a previous build exist at "{0}" and cannot be deleted, bad. Reason: {1}.'
					.format( directory, e ) )
		try:
			os.makedirs( directory )
		except ( OSError, IOError )as e:
			raise ConfigurationError( 'Cannot create required build directory "{0}"!'.format( directory ) )
		mApp().message( self, 'starting build job for project "{0}" at revision {1}.'
					.format( buildInfo.getProjectName(), rev ) )
		with EnvironmentSaver():
			os.chdir( directory )
			extend_debug_prefix( buildInfo.getProjectName() )
			iface = BuildScriptInterface( os.path.abspath( buildInfo.getBuildScript() ) )
			runner = iface.execute( revision = rev, url = buildInfo.getUrl(), buildType = buildType )
			try:
				with open( 'buildscript.log', 'w' ) as f:
					text = runner.getStdOut() or b''
					f.write( text.decode() )
			except Exception as e:
				mApp().message( self, 'Problem! saving the build script output failed during handling an exception! {0}'
					.format( e ) )
			if runner.getReturnCode() != 0:
				mApp().message( self, 'build failed for project "{0}" at revision {1}'.format( buildInfo.getProjectName(), rev ) )
				# FIXME send out email reports on configuration or MOM errors
				mApp().message( self, 'exit code {0}'.format( runner.getReturnCode() ) )
				print( """\
-->   ____        _ _     _   _____     _ _          _ 
-->  | __ ) _   _(_) | __| | |  ___|_ _(_) | ___  __| |
-->  |  _ \| | | | | |/ _` | | |_ / _` | | |/ _ \/ _` |
-->  | |_) | |_| | | | (_| | |  _| (_| | | |  __/ (_| |
-->  |____/ \__,_|_|_|\__,_| |_|  \__,_|_|_|\___|\__,_|
--> 
""" )
				return False
			else:
				mApp().message( self, 'build succeeded for project "{0}" at revision {1}'.format( buildInfo.getProjectName(), rev ) )
				print( """\
-->   _         _ _    _      _
-->  | |__ _  _(_) |__| |  __| |___ _ _  ___
-->  | '_ \ || | | / _` | / _` / _ \ ' \/ -_)
-->  |_.__/\_,_|_|_\__,_| \__,_\___/_||_\___|
--> 
""" )
				return True

	def getNewestBuildInfo( self, buildScript ):
		connection = self.getConnection()
		try:
			cursor = connection.cursor()
			query = 'select * from {0} where script=? order by id desc limit 1'.format( BuildStatus.TableName )
			cursor.execute( query, [ buildScript ] )
			for row in cursor:
				buildInfo = self.__makeBuildInfoFromRow( row )
				return buildInfo # only the first (and only) result is interesting
		finally:
			cursor.close()

	def getBuildInfoForInitialRevision( self, buildScript, projectName ):
		iface = BuildScriptInterface( buildScript )
		revision = iface.queryCurrentRevision()
		buildInfo = BuildInfo()
		buildInfo.setProjectName( projectName )
		buildInfo.setBuildStatus( BuildInfo.Status.InitialRevision )
		buildInfo.setRevision( revision )
		buildInfo.setBuildScript( buildScript )
		return buildInfo

	def getBuildInfoForRevisionsSince( self, buildScript, projectName, revision ):
		'''Return all revisions that modified the project since the specified revision.
		@return a list of BuildInfo object, with the latest commit last
		@throws MomEception, if any of the operations fail
		'''
		iface = BuildScriptInterface( buildScript )
		buildInfos = []
		lines = iface.queryRevisionsSince( revision )
		for line in lines:
			line = line.strip()
			if not line:
				continue

			parts = line.split( ' ' )
			if len( parts ) != 3:
				MomError( 'Error in build script output in line "{0}"'.format( line ) )

			buildInfo = BuildInfo()
			buildInfo.setProjectName( projectName )
			buildInfo.setBuildStatus( buildInfo.Status.NewRevision )
			buildInfo.setBuildType( parts[0] )
			buildInfo.setRevision( parts[1] )
			buildInfo.setUrl( parts[2] )
			buildInfo.setBuildScript( buildScript )
			buildInfos.append( buildInfo )

		buildInfos.reverse()
		return buildInfos

	def takeBuildInfoAndBuild( self, buildScripts ):
		'''Take a new revision from the build job list. Mark it as pending, and build it. Mark it as done afterwards.'''
		buildInfo = None
		with self.getConnection() as conn:
			buildInfos = self._loadBuildInfo( conn, BuildInfo.Status.NewRevision )
			for build in buildInfos:
				# the list is ordered by priority
				if os.path.normpath( os.path.abspath( build.getBuildScript() ) ) in buildScripts:
					build.setBuildStatus( BuildInfo.Status.Pending )
					self._updateBuildInfo( conn, build )
					buildInfo = build
					break
		if not buildInfo:
			return False
		try:
			self.performBuild( buildInfo )
		finally:
			with self.getConnection() as conn:
				buildInfo.setBuildStatus( BuildInfo.Status.Completed )
				self._updateBuildInfo( conn, buildInfo )
		return True
