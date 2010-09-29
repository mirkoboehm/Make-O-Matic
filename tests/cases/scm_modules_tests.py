# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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
from core.Build import Build
import shutil
import os
from tests.helpers.MomTestCase import MomTestCase
from datetime import datetime

class ScmModulesTests ( MomTestCase ):

	GIT_EXAMPLE = 'git://github.com/KDAB/Make-O-Matic.git'
	SVN_EXAMPLE = 'http://ratproxy.googlecode.com/svn/trunk/'

	def setUp( self ):
		MomTestCase.setUp( self, False )
		self.build = Build()
		self.project = Project( 'ScmFactoryTest' )
		self.build.setProject( self.project )

	def tearDown( self ):
		MomTestCase.tearDown( self )
		os.chdir( ".." )
		shutil.rmtree( "None" )

	def _initialize( self, scmUrl ):
		self.project.createScm( scmUrl )

		self.build.getParameters().parse()
		self.build.initialize()
		self.build.runPreFlightChecks()
		self.build.runSetups()

	def _validateRevisionInfoContent( self ):
		# TODO: Add better tests
		info = self.project.getScm().getRevisionInfo()
		self.assertNotEquals( info.committerName, None )
		self.assertNotEquals( info.commitMessage, None )
		self.assertNotEquals( info.commitTime, None )
		self.assertNotEquals( info.revision, None )

	def testScmGit( self ):
		self._initialize( self.GIT_EXAMPLE )
		self._validateRevisionInfoContent()

	def testScmSvn( self ):
		self._initialize( self.SVN_EXAMPLE )
		self._validateRevisionInfoContent()

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
		self.assertEqual( info1.revision, info2.revision )


if __name__ == "__main__":
	unittest.main()
