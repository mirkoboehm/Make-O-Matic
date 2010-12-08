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

from tests.helpers.MomTestCase import MomTestCase
import os
import unittest
import sys
import shutil
import glob
from core.MApplication import MApplication
from buildcontrol.simple_ci import Parameters
from buildcontrol.simple_ci.Slave import Slave
from tests.helpers.TestUtils import md5sum
from core.helpers.SafeDeleteTree import rmtree

class SimpleCITests( MomTestCase ):
	'''SimpleCITests executes the simple_ci tool in different ways.'''

	ThisFilePath = os.path.realpath( os.path.dirname( __file__ ) )
	BuildScriptName = os.path.join( ThisFilePath, '..', 'buildscripts', 'example_mom_buildscript.py' )
	SyntaxErrorBuildScriptName = os.path.join( ThisFilePath, '..', 'buildscripts', 'syntax-error.py' )
	ToolName = os.path.join( ThisFilePath, '..', '..', 'tools', 'simple_ci.py' )
	CurrentDirectory = os.getcwd()

	DatabaseChecksum = None

	def setUp( self ):
		MomTestCase.setUp( self )

		# save current database checksum for later comparison, check if database file exists (e.g. at first run)
		if os.path.exists( self._getSimpleCiDatabaseFilename() ):
			self.DatabaseChecksum = md5sum( self._getSimpleCiDatabaseFilename() )

	def tearDown( self ):
		MomTestCase.tearDown( self )

		# make sure config content stayed the same
		if self.DatabaseChecksum:
			self.assertEqual( self.DatabaseChecksum, md5sum( self._getSimpleCiDatabaseFilename() ),
					"Database changed during tests run." )

		os.chdir( self.CurrentDirectory )
		removeDirectories = glob.glob( "make-o-matic*" )
		removeDirectories.extend( glob.glob( "builds" ) )
		for directory in removeDirectories:
			rmtree( directory )

	# get the SimpleCI database file path by instantiating an SimpleCiBase instance
	def _getSimpleCiDatabaseFilename( self ):
		# we need to replace the MApplication instance
		oldInstance = MApplication.instance
		MApplication.instance = None

		# instantiate SimpleCiBase instance
		params = Parameters.Parameters()
		params.parse()
		simpleCiInstance = Slave( params )
		databaseFilename = os.path.join( simpleCiInstance.getDataDir(), 'buildstatus.sqlite' )

		# reset MApplication instance
		MApplication.instance = oldInstance
		return databaseFilename

	def testUsageHelp( self ):
		cmd = [ sys.executable, SimpleCITests.ToolName, '-h' ]
		runner = self.runCommand( cmd, 'simple_ci usage help' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testSlaveRunFindRevisions( self ):
		cmd = [ sys.executable, SimpleCITests.ToolName, '--slave',
			'--pause', '1', '-b', SimpleCITests.BuildScriptName ]
		runner = self.runCommand( cmd, 'simple_ci slave find revisions' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testSlaveRunPerformBuilds( self ):
		cmd = [ sys.executable, SimpleCITests.ToolName, '--slave',
			'--pause', '1', '-f', SimpleCITests.BuildScriptName ]
		runner = self.runCommand( cmd, 'simple_ci slave find revisions' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testSlaveRunFindRevisionsSyntaxError( self ):
		cmd = [ sys.executable, SimpleCITests.ToolName, '--slave',
			'--pause', '1', '-b', SimpleCITests.SyntaxErrorBuildScriptName ]
		runner = self.runCommand( cmd, 'simple_ci slave find revisions, build script syntax error' )
		# simple_ci is supposed to work with broken build scripts
		# more tests in buildscript_interface_tests
		self.assertEquals( runner.getReturnCode(), 0 )

if __name__ == "__main__":
	unittest.main()
