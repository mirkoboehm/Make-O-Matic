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
from core.MObject import MObject
import sqlite3
from buildcontrol.common.BuildInfo import BuildInfo

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

	def saveBuildInfo( self, buildInfos ):
		conn = self.getConnection()
		try:
			c = conn.cursor()
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
				c.execute( query, values )
				buildInfo.setBuildId( c.lastrowid )
			conn.commit()
		finally:
			c.close()

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

	def getNewestBuildInfo( self, buildScript ):
		conn = self.getConnection()
		try:
			c = conn.cursor()
			query = 'select * from {0} where script=? order by id desc limit 1'.format( BuildStatus.TableName )
			c.execute( query, [ buildScript ] )
			for row in c:
				buildInfo = self.__makeBuildInfoFromRow( row )
				return buildInfo # only the first (and only) result is interesting
		finally:
			c.close()

	def loadBuildInfo( self, status = BuildInfo.Status.NewRevision ):
		'''Load all BuildInfo objects from the database that are in the specified status.'''
		conn = self.getConnection()
		try:
			c = conn.cursor()
			query = 'select * from {0} where status=? order by priority desc'.format( BuildStatus.TableName )
			c.execute( query, [ status ] )
			buildInfos = []
			for row in c:
				buildInfo = self.__makeBuildInfoFromRow( row )
				buildInfos.append( buildInfo )
			return buildInfos
		finally:
			c.close()

