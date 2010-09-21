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
from core.modules.scm.Factory import SourceCodeProviderFactory
import os

class RemoteBuilder( MObject ):
	def __init__( self, revisionInfo = None, location = None, path = None, script = None, name = None ):
		MObject.__init__( self, name )
		self.setRevisionInfo( revisionInfo )
		self.setBuildscript( script )
		self.setLocation( location )
		self.setPath( path )

	def setRevisionInfo( self, revInfo ):
		self.__revisionInfo = revInfo

	def getRevisionInfo( self ):
		return self.__revisionInfo

	def setLocation( self, location ):
		self.__location = location

	def getLocation( self ):
		return self.__location

	def setPath( self, path ):
		self.__path = path

	def getPath( self ):
		return self.__path

	def setBuildscript( self, script ):
		self.__buildscript = script

	def getBuildscript( self ):
		return self.__buildscript

	def fetchBuildScript( self ):
		# create SCM implementation:
		scm = SourceCodeProviderFactory().makeScmImplementation( self.getLocation() )
		localFolder = os.path.join( os.getcwd(), 'temp-mom_tests' )
		remoteFolder = 'admin'
		scm.fetchRepositoryFolder( remoteFolder, localFolder )

