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
from tests.helpers.MomTestCase import MomTestCase
import os
from buildcontrol.common.BuildScriptInterface import BuildScriptInterface
from core.Settings import Settings
import unittest

class CharmBuildTests( MomTestCase ):
	'''CharmBuildTests executes the example_charm build script with revisions known to work.'''

	BuildScriptName = os.path.join( 'buildscripts', 'example_charm.py' )

	def test_aaa_queryProjectName( self ):
		iface = BuildScriptInterface( CharmBuildTests.BuildScriptName )
		self.assertTrue( iface.querySetting( Settings.ProjectName ) )

if __name__ == "__main__":
	unittest.main()
