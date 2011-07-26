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

from mom.apps.common.BuildInfo import BuildInfo
from mom.apps.common.BuildStatus import BuildStatus
from tempfile import NamedTemporaryFile
from mom.tests.helpers.MomTestCase import MomTestCase
import os
import random
import string
import unittest

class BuildStatusPersistenceTests( MomTestCase ):

	def _randomString( self, length = 8 ):
		return ''.join( random.choice( string.ascii_uppercase + string.digits ) for x in range( 8 ) ) #@UnusedVariable

	def testPersistBuildInfo( self ):
		randomBranch = self._randomString()
		randomTag = self._randomString()
		status = BuildStatus()
		filename = NamedTemporaryFile( suffix = '.sqlite' ).name
		status.setDatabaseFilename( filename )
		info = BuildInfo()
		info.setProjectName( status.getName() )
		info.setPriority( 0 )
		info.setBuildStatus( BuildInfo.Status.NewRevision )
		info.setBuildType( 'm' )
		info.setRevision( 'abcdef' )
		info.setUrl( '0123456789' )
		info.setBranch( randomBranch )
		info.setTag( randomTag )
		info.setBuildScript( 'dummy.py' )
		status.saveBuildInfo( [ info ] )
		revs = status.loadBuildInfo( BuildInfo.Status.NewRevision )
		self.assertTrue( len( revs ) == 1 )
		self.assertEqual( revs[0].__dict__, info.__dict__ )
		os.remove( filename )

	def testParsingPrintableRepresentation( self ):
		info = BuildInfo()
		info.setBuildType( self._randomString() )
		info.setPriority( 3 )
		info.setProjectName( self._randomString() )
		info.setRevision( self._randomString() )
		info.setUrl( self._randomString() )
		info.setBranch( self._randomString() )
		info.setTag( self._randomString() )
		stringRepresentation = info.printableRepresentation()
		result = BuildInfo()
		result.initializeFromPrintableRepresentation( stringRepresentation )
		self.assertEqual( info.__dict__, result.__dict__ )

if __name__ == "__main__":
	unittest.main()
