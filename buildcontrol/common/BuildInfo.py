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
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, check_for_nonnegative_int_or_none, check_for_int_or_none
import re
from core.Exceptions import MomError

class BuildInfo( MObject ):
	'''BuildInfo represents a single build script run.'''
	LineIdentifier = 'revision'

	class Status( object ):
		# pylint: disable-msg=r0903
		# Ignore this as we're just simulating an enum so don't need public members
		NoStatus, NewRevision, Pending, Completed, InitialRevision, Cancelled = range( 6 )

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		self.setBuildId( None )
		self.setProjectName( None )
		self.setPriority( None )
		self.setBuildStatus( BuildInfo.Status.NoStatus )
		self.setBuildType( None )
		self.setRevision( None )
		self.setUrl( None )
		self.setBranch( None )
		self.setTag( None )
		self.setBuildScript( None )

	def getProjectName( self ):
		return self.__projectName

	def setProjectName( self, name ):
		check_for_nonempty_string_or_none( name, 'The project name should not be empty!' )
		self.__projectName = name

	def getBuildId( self ):
		return self.__buildId

	def setBuildId( self, buildId ):
		check_for_nonnegative_int_or_none( buildId, 'The build id needs to be a non-negative integer!' )
		self.__buildId = buildId

	def setPriority( self, priority ):
		check_for_int_or_none( priority, 'The priority should be an integer number!' )
		self.__priority = priority

	def getPriority( self ):
		return self.__priority

	def setBuildStatus( self, status ):
		self.__buildStatus = status

	def getBuildStatus( self ):
		return self.__buildStatus

	def getBuildType( self ):
		return self.__buildType

	def setBuildType( self, buildType ):
		self.__buildType = buildType

	def getRevision( self ):
		return self.__revision

	def setRevision( self, revision ):
		self.__revision = revision

	def getUrl( self ):
		return self.__url

	def setUrl( self, url ):
		self.__url = url

	def setBranch( self, branch ):
		check_for_nonempty_string_or_none( branch, 'The branch should be a string!' )
		self.__branch = branch

	def getBranch( self ):
		return self.__branch

	def setTag( self, tag ):
		check_for_nonempty_string_or_none( tag, 'The tag should be a string!' )
		self.__tag = tag

	def getTag( self ):
		return self.__tag

	def getBuildScript( self ):
		return self.__buildScript

	def setBuildScript( self, script ):
		self.__buildScript = script

	def printableRepresentation( self ):
		values = {
			'buildtype' : self.getBuildType(),
			'priority' : self.getPriority(),
			'project' : self.getProjectName(),
			'revision' : self.getRevision(),
			'url' : self.getUrl(),
			'branch' : self.getBranch(),
			'tag' : self.getTag()
		}
		# Do not use repr() directly, the Pydev debugger overloads it to shorten the results.
		# As a result, tests fail when run within Eclipse.
		representation = values.__repr__()
		return format( '{0}: {1}'.format( BuildInfo.LineIdentifier, representation ) )

	def initializeFromPrintableRepresentation( self, line ):
		match = re.match( '^{0}: (.+)$'.format( BuildInfo.LineIdentifier ), line )
		if not match:
			raise MomError( 'Unable to parse revision description "{0}"'.format( line ) )
		representation = match.group( 1 )
		if not representation:
			raise MomError( 'Malformated revision description "{0}"'.format( line ) )
		# FIXME parse errors?
		dictionary = eval( representation )
		self.setBuildType( dictionary[ 'buildtype' ] )
		self.setPriority( dictionary[ 'priority' ] )
		self.setProjectName( dictionary[ 'project'] )
		self.setRevision( dictionary['revision'] )
		self.setUrl( dictionary['url'] )
		self.setBranch( dictionary['branch'] )
		self.setTag( dictionary['tag'] )
