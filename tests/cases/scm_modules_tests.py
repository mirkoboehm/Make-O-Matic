# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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
from core.MApplication import MApplication
from core.Project import Project
from core.Build import Build

class ScmModulesTests ( unittest.TestCase ):

	def setUp( self ):
		if MApplication.instance:
			# do not try this at home!
			MApplication.instance = None

		self.build = Build()
		self.project = Project( 'ScmFactoryTest' )
		self.build.setProject( self.project )

	def tearDown( self ):
		MApplication.instance = None

	def _initializeBuild( self ):
		"""Create project checkout-step (required)"""

		self.build.getParameters().parse()
		self.build.initialize()
		self.build.runPreFlightChecks()
		self.build.runSetups()

	def testScmGit( self ):
		self.project.createScm( 'git:git://gitorious.org/make-o-matic/mom.git' )
		scm = self.project.getScm()
		self._initializeBuild()

		# run scm step only 
		scm.getInstructions().execute()

		# TODO: Add better tests
		info = scm.getRevisionInfo()
		self.assertNotEquals( info.committer, None )
		self.assertNotEquals( info.commitMessage, None )
		self.assertNotEquals( info.commitTime, None )
		self.assertNotEquals( info.revision, None )

	def testScmSvn( self ):
		self.project.createScm( 'svn:http://ratproxy.googlecode.com/svn/trunk/' ) # random light-weight repository
		scm = self.project.getScm()
		self._initializeBuild()

		# run scm step only 
		scm.getInstructions().execute()

		# TODO: Add better tests
		info = scm.getRevisionInfo()
		self.assertNotEquals( info.committer, None )
		self.assertNotEquals( info.commitMessage, None )
		self.assertNotEquals( info.commitTime, None )
		self.assertNotEquals( info.revision, None )

if __name__ == "__main__":
	unittest.main()
