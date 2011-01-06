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
from core.helpers.SCMUidMapper import SCMUidSvnAuthorsFileMap
import os.path

class ScmModulesTests ( MomBuildMockupTestCase ):

	GIT_EXAMPLE = 'git://github.com/defunkt/hub.git'
	SVN_EXAMPLE = 'http://googletest.googlecode.com/svn/'

	def _initialize( self, scmUrl, revision = None, branch = None, tag = None ):
		self.project.createScm( scmUrl )

		if revision:
			self.project.getScm().setRevision( revision )

		if branch:
			self.project.getScm().setBranch( branch )

		if tag:
			self.project.getScm().setTag( tag )

		self.build.getParameters().parse()
		self.build.initialize()
		self.build.runPrepare()
		self.build.runPreFlightChecks()
		self.build.runSetups()

	def _validateRevisionInfoContent( self, info ):
		# TODO: Add better tests
		self.assertNotEquals( info.committerName, None )
		self.assertNotEquals( info.commitMessage, None )
		self.assertNotEquals( info.commitTime, None )
		self.assertNotEquals( info.commitTimeReadable, None )
		self.assertNotEquals( info.revision, None )

	def testScmUidMapperWithAuthorsMap( self ):
		self._initialize( self.SVN_EXAMPLE )
		scm = self.project.getScm()
		mapper = scm.getSCMUidMapper()
		fileMap = SCMUidSvnAuthorsFileMap( os.path.join( self.TEST_DATA_DIRECTORY, 'svn-authors-map-example.txt' ) )
		mapper.addMapping( fileMap )
		email = mapper.getEmail( "kevin.funk" )
		self.assertNotEquals( email, None )

	def testScmGit( self ):
		self._initialize( self.GIT_EXAMPLE )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )
		self.assertNotEquals( info.shortRevision, None, "Git should have a short revision" )

	def testScmGitRevision( self ):
		self._initialize( self.GIT_EXAMPLE, revision = "c2e575fa09b2e90a9108" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmGitShortRevision( self ):
		self._initialize( self.GIT_EXAMPLE, revision = "c2e575" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmGitBranch( self ):
		self._initialize( self.GIT_EXAMPLE, branch = "gh-pages" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmGitTag( self ):
		self._initialize( self.GIT_EXAMPLE, tag = "v1.4.1" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmSvn( self ):
		self._initialize( self.SVN_EXAMPLE )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )
		self.assertEquals( info.shortRevision, None, "Subversion should not have a short revision" )

	def testScmSvnRevision( self ):
		self._initialize( self.SVN_EXAMPLE, revision = "246" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmSvnBranch( self ):
		# FIXME Mike: The branch "release-1.5" that this was referring to is gone!
		self._initialize( self.SVN_EXAMPLE, branch = "unsupported-vc6-port" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmSvnTag( self ):
		self._initialize( self.SVN_EXAMPLE, tag = "release-1.5.0" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmSvnRevisionInfoCache( self ):
		self._initialize( self.SVN_EXAMPLE )

		scm = self.project.getScm()
		scm.setRevision( 246 ) # set revision explicitly, HEAD revision info isn't cached
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
