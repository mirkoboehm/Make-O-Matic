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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from buildcontrol.common.BuildScriptInterface import BuildScriptInterface
from tests.helpers.MomTestCase import MomTestCase
import os
from core.Settings import Settings
import unittest
from core.helpers.GlobalMApp import mApp
import shutil
from core.Exceptions import MomError

class BuildScriptInterfaceTests( MomTestCase ):

	ThisFilePath = os.path.realpath( os.path.dirname( __file__ ) )
	BuildScriptName = os.path.join( ThisFilePath, '..', 'buildscripts', 'example_mom_buildscript.py' )
	SyntaxErrorBuildScriptName = os.path.join( ThisFilePath, '..', 'buildscripts', 'syntax-error.py' )

	def setUp( self ):
		MomTestCase.setUp( self )
		self.iface = BuildScriptInterface( BuildScriptInterfaceTests.BuildScriptName )

	def tearDown( self ):
		MomTestCase.tearDown( self )
		if os.path.exists( "make-o-matic" ):
			#FIXME Try and delete directory twice (if needed) to work around stupid Windows race condition
			shutil.rmtree( "make-o-matic", True )
			if os.path.exists( "make-o-matic" ):
				shutil.rmtree( "make-o-matic", False )

	def testQuerySetting( self ):
		variable = self.iface.querySetting( Settings.MomVersionNumber )
		self.assertEquals( variable, mApp().getSettings().get( Settings.MomVersionNumber ) )

	def testPrintCurrentRevision( self ):
		variable = self.iface.queryCurrentRevision()
		self.assertTrue( variable )

	def testPrintRevisionsSince( self ):
		revisions = self.iface.queryRevisionsSince( '8c758c1f1de2bcc19bda516f1acadf869ba28ee4' )
		self.assertTrue( len( revisions ) >= 5 )

	def testExecuteBuildScript( self ):
		runner = self.iface.execute( buildType = 'c', revision = 'HEAD', captureOutput = True )
		self.assertEqual( 0, runner.getReturnCode() )

	def testQueryBuildNameSyntaxError( self ):
		iface = BuildScriptInterface( BuildScriptInterfaceTests.SyntaxErrorBuildScriptName )
		try:
			iface.querySetting( Settings.ScriptBuildName )
			self.fail( 'The syntax error build script should throw an exception when printing the build name.' )
		except MomError:
			pass

	def testPrintRevisionsSinceSyntaxError( self ):
		iface = BuildScriptInterface( BuildScriptInterfaceTests.SyntaxErrorBuildScriptName )
		try:
			iface.queryRevisionsSince( '8c758c1f1de2bcc19bda516f1acadf869ba28ee4' )
			self.fail( 'The syntax error build script should throw an exception when querying recent revisions.' )
		except MomError:
			pass

	def testPrintCurrentRevisionSyntaxError( self ):
		iface = BuildScriptInterface( BuildScriptInterfaceTests.SyntaxErrorBuildScriptName )
		try:
			iface.queryCurrentRevision()
			self.fail( 'The syntax error build script should throw an exception when querying the current revision.' )
		except MomError:
			pass

if __name__ == "__main__":
	unittest.main()
