# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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
from datetime import datetime
from tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase

class ScmModulesTests ( MomBuildMockupTestCase ):

	GIT_EXAMPLE = 'git://github.com/KDAB/Make-O-Matic.git'
	SVN_EXAMPLE = 'http://ratproxy.googlecode.com/svn/trunk/'

	def setUp( self ):
		MomBuildMockupTestCase.setUp( self )

	def tearDown( self ):
		MomBuildMockupTestCase.tearDown( self )

	def _initialize( self, scmUrl ):
		self.project.createScm( scmUrl )

		self.build.getParameters().parse()
		self.build.initialize()
		self.build.runPreFlightChecks()
		self.build.runSetups()

	def _validateRevisionInfoContent( self, info ):
		# TODO: Add better tests
		self.assertNotEquals( info.committerName, None )
		self.assertNotEquals( info.commitMessage, None )
		self.assertNotEquals( info.commitTime, None )
		self.assertNotEquals( info.commitTimeReadable, None )
		self.assertNotEquals( info.revision, None )

	def testScmGit( self ):
		self._initialize( self.GIT_EXAMPLE )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )
		self.assertNotEquals( info.shortRevision, None, "Git should short revision" )

	def testScmSvn( self ):
		self._initialize( self.SVN_EXAMPLE )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )
		self.assertEquals( info.shortRevision, None, "Svn should not have short revision" )

	def testScmSvnRevisionInfoCache( self ):
		self._initialize( self.SVN_EXAMPLE )

		scm = self.project.getScm()
		scm.setRevision( 9 ) # set revision explicitly, HEAD revision info isn't cached
		info1 = scm.getRevisionInfo()

		# test if cache is working
		startTime = datetime.utcnow()
		info2 = scm.getRevisionInfo()
		stopTime = datetime.utcnow()
		delta = stopTime - startTime
		self.assertTrue( delta.microseconds < 1000, "Fetching revision info for a cached revision took too long" )

		# also test if info is the same
		self.assertEqual( info1.committerName, info2.committerName )
		self.assertEqual( info1.commitMessage, info2.commitMessage )
		self.assertEqual( info1.commitTime, info2.commitTime )
		self.assertEqual( info1.commitTimeReadable, info2.commitTimeReadable )
		self.assertEqual( info1.revision, info2.revision )

if __name__ == "__main__":
	unittest.main()
