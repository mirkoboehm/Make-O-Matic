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
import unittest
import sys

class SimpleCITests( MomTestCase ):
	'''SimpleCITests executes the simple_ci tool in different ways.'''

	BuildScriptName = os.path.join( 'buildscripts', 'example_mom_buildscript.py' )
	ToolName = os.path.join( '..', 'tools', 'simple_ci.py' )

	def testUsageHelp( self ):
		cmd = '{0} {1} -h'.format( sys.executable, SimpleCITests.ToolName )
		runner = self.runCommand( cmd, 'simple_ci usage help' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testSlaveRunFindRevisions( self ):
		cmd = '{0} {1} --slave --pause 1 -b {2}'.format( 
			sys.executable,
			SimpleCITests.ToolName,
			SimpleCITests.BuildScriptName )
		runner = self.runCommand( cmd, 'simple_ci slave find revisions' )
		self.assertEquals( runner.getReturnCode(), 0 )

	def testSlaveRunPerformBuilds( self ):
		cmd = '{0} {1} --slave --pause 1 -f {2}'.format( 
			sys.executable,
			SimpleCITests.ToolName,
			SimpleCITests.BuildScriptName )
		runner = self.runCommand( cmd, 'simple_ci slave find revisions' )
		self.assertEquals( runner.getReturnCode(), 0 )

if __name__ == "__main__":
	unittest.main()
