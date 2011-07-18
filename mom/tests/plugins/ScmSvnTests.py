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

from buildcontrol.common.BuildInfo import BuildInfo
from core.Defaults import Defaults
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.helpers.SCMUidMapper import SCMUidSvnAuthorsFileMap
from datetime import datetime
from mom.tests.helpers.ScmTestCase import ScmTestCase
import os.path
import unittest

class ScmSvnTests ( ScmTestCase ):

	SVN_EXAMPLE = 'http://googletest.googlecode.com/svn/'

	def testScmUidMapperWithAuthorsMap( self ):
		self._initialize( self.SVN_EXAMPLE )
		scm = self.project.getScm()
		mapper = scm.getSCMUidMapper()
		fileMap = SCMUidSvnAuthorsFileMap( os.path.join( self.TEST_DATA_DIRECTORY, 'svn-authors-map-example.txt' ) )
		mapper.addMapping( fileMap )
		email = mapper.getEmail( "kevin.funk" )
		self.assertNotEquals( email, None )

	def testScmSvn( self ):
		self._initialize( self.SVN_EXAMPLE )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmSvnRevision( self ):
		self._initialize( self.SVN_EXAMPLE, revision = "246" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )

	def testScmSvnBranch( self ):
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

	def __scmSvnBranchCommitParserTestHelper( self, summarizedDiff ):
		# locsl location to build type mapping for the test:
		LocationBuildTypeMap = [
			[ '/trunk', Defaults.BranchType_Master, 'C' ],
			[ '/branches/work', Defaults.BranchType_Branch, 'C' ],
			[ '/branches/release', Defaults.BranchType_Branch, 'S' ],
			[ '/branches', Defaults.BranchType_Branch, 'C' ],
			[ '/tags/old', Defaults.BranchType_Tag, 'C' ],
			[ '/tags', Defaults.BranchType_Tag, 'S' ]
		]
		url = 'file:///repo/project'
		self._initialize( self.SVN_EXAMPLE )
		scm = self.project.getScm()
		scm.setUrl( url )
		# set up input BuildInfo object:
		buildInfo = BuildInfo()
		buildInfo.setProjectName( 'scm_modules_test' )
		buildInfo.setBuildType( 'C' )
		buildInfo.setRevision( 4711 )
		buildInfo.setUrl( url )
		return buildInfo, scm._splitIntoBuildInfos( buildInfo, summarizedDiff, LocationBuildTypeMap )

	def testScmSvnBranchCommitParsingOneFileTrunk( self ):
		summarizedDiff = [ 'M    file:///repo/project/trunk/README' ]
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		self.assertEqual( len( buildInfos ), 1 )
		info = buildInfos[0]
		self.assertTrue( isinstance( info, BuildInfo ) )
		self.assertEqual( info.getRevision(), buildInfo.getRevision() )
		self.assertEqual( info.getUrl(), buildInfo.getUrl() )
		self.assertEqual( info.getBranch(), None )
		self.assertEqual( info.getTag(), None )

	def testScmSvnBranchCommitParsingOneFileBranchA( self ):
		summarizedDiff = [ 'M    file:///repo/project/branches/A/README' ]
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		self.assertEqual( len( buildInfos ), 1 )
		info = buildInfos[0]
		self.assertTrue( isinstance( info, BuildInfo ) )
		self.assertEqual( info.getRevision(), buildInfo.getRevision() )
		self.assertEqual( info.getUrl(), buildInfo.getUrl() )
		self.assertEqual( info.getBranch(), 'A' )
		self.assertEqual( info.getTag(), None )

	def testScmSvnBranchCommitParsingOneFileBranchReleaseA( self ):
		summarizedDiff = [ 'M    file:///repo/project/branches/release/A/README' ]
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		self.assertEqual( len( buildInfos ), 1 )
		info = buildInfos[0]
		self.assertTrue( isinstance( info, BuildInfo ) )
		self.assertEqual( info.getRevision(), buildInfo.getRevision() )
		self.assertEqual( info.getUrl(), buildInfo.getUrl() )
		self.assertEqual( info.getBranch(), 'release/A' )
		self.assertEqual( info.getTag(), None )

	def testScmSvnBranchCommitParsingNoFileBranch( self ):
		summarizedDiff = [ 'M    file:///repo/project/branches' ] # branches needs to be created at some point, too :-)
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		buildInfo = buildInfo # make checker happy
		self.assertEqual( len( buildInfos ), 0 )

	def testScmSvnBranchCommitParsingOneFileTagOldA( self ):
		summarizedDiff = [ 'M    file:///repo/project/tags/old/A/README' ]
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		self.assertEqual( len( buildInfos ), 1 )
		info = buildInfos[0]
		self.assertTrue( isinstance( info, BuildInfo ) )
		self.assertEqual( info.getRevision(), buildInfo.getRevision() )
		self.assertEqual( info.getUrl(), buildInfo.getUrl() )
		self.assertEqual( info.getBranch(), None )
		self.assertEqual( info.getTag(), 'old/A' )

	def testScmSvnBranchCommitParsingOneFileTagDeprecatedB( self ):
		# Failing test: 'rotten' is not a configured tag prefix.
		# Therefore the correctly detected tag name is 'rotten', not 'rotten/B'.'''

		summarizedDiff = [ 'M    file:///repo/project/tags/rotten/B/README' ]
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		buildInfo = buildInfo # make checker happy
		self.assertEqual( len( buildInfos ), 1 )
		info = buildInfos[0]
		self.assertTrue( isinstance( info, BuildInfo ) )
		self.assertEqual( info.getRevision(), buildInfo.getRevision() )
		self.assertEqual( info.getUrl(), buildInfo.getUrl() )
		self.assertEqual( info.getBranch(), None )
		self.assertEqual( info.getTag(), 'rotten' )

	def testScmSvnBranchCommitParsingOneFileTagA( self ):
		summarizedDiff = [ 'M    file:///repo/project/tags/A-1.0.0/README' ]
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		self.assertEqual( len( buildInfos ), 1 )
		info = buildInfos[0]
		self.assertTrue( isinstance( info, BuildInfo ) )
		self.assertEqual( info.getRevision(), buildInfo.getRevision() )
		self.assertEqual( info.getUrl(), buildInfo.getUrl() )
		self.assertEqual( info.getBranch(), None )
		self.assertEqual( info.getTag(), 'A-1.0.0' )

	def testScmSvnBranchCommitParsingFourFilesTrunk( self ):
		summarizedDiff = [
			'M    file:///repo/project/trunk/README',
			'M    file:///repo/project/trunk/admin/buildscript.py',
			'M    file:///repo/project/trunk/src/SomeClass.h',
			'M    file:///repo/project/trunk/src/SomeClass.cpp'
		]
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		self.assertEqual( len( buildInfos ), 1 )
		info = buildInfos[0]
		self.assertTrue( isinstance( info, BuildInfo ) )
		self.assertEqual( info.getRevision(), buildInfo.getRevision() )
		self.assertEqual( info.getUrl(), buildInfo.getUrl() )
		self.assertEqual( info.getBranch(), None )
		self.assertEqual( info.getTag(), None )

	def testScmSvnBranchCommitParsingFourFilesThreeLocations( self ):
		summarizedDiff = [
			'M    file:///repo/project/trunk/README',
			'M    file:///repo/project/tags/A-1.0.0/README',
			'M    file:///repo/project/branches/A/README'
		]
		buildInfo, buildInfos = self.__scmSvnBranchCommitParserTestHelper( summarizedDiff )
		self.assertEqual( len( buildInfos ), 3 )
		# test common attributes (the other should be tested individually in other tests):
		for info in buildInfos:
			self.assertTrue( isinstance( info, BuildInfo ) )
			self.assertEqual( info.getRevision(), buildInfo.getRevision() )
			self.assertEqual( info.getUrl(), buildInfo.getUrl() )

	def __branchnameBuildtypeMappingTestHelper( self, branchType, branchName ):
		mapping = [
			# branch type, name regular expression, build type
			[ Defaults.BranchType_Branch, '.+-release$', 'S' ],
			[ Defaults.BranchType_Branch, '.+-work$', 'C' ]
		]
		mApp().getSettings().set( Settings.SCMSvnBranchNameBuildTypeMap, mapping )
		url = 'file:///repo/project'
		self._initialize( self.SVN_EXAMPLE )
		scm = self.project.getScm()
		scm.setUrl( url )
		buildInfo = BuildInfo()
		buildInfo.setProjectName( 'scm_modules_test' )
		buildInfo.setBuildType( 'E' )
		buildInfo.setRevision( 4711 )
		buildInfo.setBranch( branchName )
		buildInfo.setUrl( url )
		scm._applyBranchnameBuildtypeMapping( branchType, buildInfo )
		return buildInfo

	def testScmSvnBranchnameBuildtypeMappingRelease( self ):
		buildInfo = self.__branchnameBuildtypeMappingTestHelper( Defaults.BranchType_Branch, 'a-1.0.0-release' )
		self.assertEqual( buildInfo.getBuildType(), 'S' )

	def testScmSvnBranchnameBuildtypeMappingWork( self ):
		buildInfo = self.__branchnameBuildtypeMappingTestHelper( Defaults.BranchType_Branch, 'a-0.9.7-work' )
		self.assertEqual( buildInfo.getBuildType(), 'C' )

	def testScmSvnBranchnameBuildtypeMappingTag( self ):
		# there is no mapping for tags, so nothing should be applied
		buildInfo = self.__branchnameBuildtypeMappingTestHelper( Defaults.BranchType_Tag, 'a-1.0.0-release' )
		self.assertEqual( buildInfo.getBuildType(), 'E' )

	def testScmSvnBranchnameBuildtypeMappingTrunk( self ):
		# build types are not applied for the master branch, so nothing should be applied
		buildInfo = self.__branchnameBuildtypeMappingTestHelper( Defaults.BranchType_Master, 'a-1.0.0-release' )
		self.assertEqual( buildInfo.getBuildType(), 'E' )

if __name__ == "__main__":
	unittest.main()
