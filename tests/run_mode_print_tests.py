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
import unittest
from core.Project import Project
from core.Settings import Settings
from test.test_iterlen import len

class RunModePrintTests( unittest.TestCase ):

	def testPrintRevisionsSince( self ):
		result = self._getRevisions( '57307ee83930c089d0eb9b4e7342c87784257071', 1 )
		self.assertEqual( len( result ), 1, 'The test asked for only one revision to be listed.' )
		line = result[0]
		self.assertEqual( line[1], '6647cbb26cf8cc511ffa541a090030fe0613172c',
			'The next revision after 57307ee83930c089d0eb9b4e7342c87784257071 should be 6647cbb26cf8cc511ffa541a090030fe0613172c' )
		self.assertEqual( line[0].lower(), 'c', 'Revision 6647cbb26cf8cc511ffa541a090030fe0613172c should be a C type build!' )

	def testPrintAllRevisionsSince( self ):
		result = self._getRevisions( '57307ee83930c089d0eb9b4e7342c87784257071' )
		self.assertTrue( len( result ) > 1, 'The test asked for only one revision to be listed.' )

	def _getRevisions( self, revision, count = None ):
		project = Project( 'ScmFactoryTest' )
		project.getSettings().set( Settings.ScriptLogLevel, 3 )
		project.createScm( 'git:git@gitorious.org:make-o-matic/mom.git' )
		if count:
			result = project.getScm()._getRevisionsSince( project, [ revision, str( count ) ] )
		else:
			result = project.getScm()._getRevisionsSince( project, [ revision ] )
		return result

if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
