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

import unittest
from mom.tests.helpers.MomTestCase import MomTestCase
from core.helpers.SettingResolver import SettingResolver
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.Exceptions import ConfigurationError
from core.helpers.FilesystemAccess import make_foldername_from_string

class SettingResolverTests( MomTestCase ):

	def testSimpleCase( self ):
		name = 'DummyTestName'
		resolver = SettingResolver( Settings.ScriptBuildName )
		mApp().getSettings().set( Settings.ScriptBuildName, name )
		self.assertEqual( name, str( resolver ) )

	def testWithDefault( self ):
		var = 'UndefinedVariable_123456'
		defaultValue = 'defaultValue value'
		resolver = SettingResolver( var, required = False, defaultValue = defaultValue )
		self.assertEqual( defaultValue, str( resolver ) )

	def testWithMissingRequiredValue( self ):
		var = 'UndefinedVariable_123456'
		defaultValue = 'defaultValue value'
		resolver = SettingResolver( var, required = True, defaultValue = defaultValue )
		try:
			str( resolver )
			self.fail( 'resolving an undefined setting should raise a ConfigurationError!' )
		except ConfigurationError:
			pass

	def testWithMissingRequiredValueDescribeMode( self ):
		var = 'UndefinedVariable_123456'
		defaultValue = 'defaultValue value'
		resolver = SettingResolver( var, required = True, defaultValue = defaultValue )
		mApp().getSettings().set( Settings.ScriptRunMode, Settings.RunMode_Describe )
		try:
			str( resolver )
		except ConfigurationError:
			self.fail( 'resolving an undefined setting in describe mode should not raise a ConfigurationError!' )

	def testWithPattern( self ):
		name = 'DummyTestName'
		pattern = 'test-{0}'
		resolver = SettingResolver( Settings.ScriptBuildName, pattern = pattern )
		mApp().getSettings().set( Settings.ScriptBuildName, name )
		self.assertEqual( pattern.format( name ), str( resolver ) )

	def testWithConvertToFolderName( self ):
		name = 'Dummy Test Name'
		result = make_foldername_from_string( name )
		resolver = SettingResolver( Settings.ScriptBuildName, convertToFolderName = True )
		mApp().getSettings().set( Settings.ScriptBuildName, name )
		self.assertEqual( result, str( resolver ) )


if __name__ == "__main__":
	unittest.main()
