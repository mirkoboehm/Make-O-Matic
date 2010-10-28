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
import unittest
from core.Project import Project
from core.Settings import Settings
from core.Build import Build
from tests.helpers.MomTestCase import MomTestCase
import os
from core.helpers.RunCommand import RunCommand

class RunModeDescribeTests( MomTestCase ):

	ThisFilePath = os.path.realpath( os.path.dirname( __file__ ) )
	BuildScriptName = os.path.join( ThisFilePath, '..', 'buildscripts', 'example_charm.py' )

	def setUp( self ):
		MomTestCase.setUp( self, False )
		self.build = Build()
		self.project = Project( 'ScmFactoryTest' )
		self.build.setProject( self.project )
		self.build.getSettings().set( Settings.ScriptLogLevel, 3 )
		self.project.createScm( 'git://github.com/KDAB/Make-O-Matic.git' )

	def testDescribe( self ):
		runner = RunCommand( [ self.BuildScriptName, '-t', 'M', 'describe' ] )
		runner.run()
		if runner.getReturnCode() != 0:
			self.fail( 'The example charm build script fails to execute in describe mode' )

if __name__ == "__main__":
	unittest.main()

