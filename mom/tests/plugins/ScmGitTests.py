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

from mom.tests.helpers.ScmTestCase import ScmTestCase
import unittest

class ScmGitTests ( ScmTestCase ):

	GIT_EXAMPLE = 'git://github.com/defunkt/hub.git'

	def testScmGit( self ):
		self._initialize( self.GIT_EXAMPLE )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )
		self.assertNotEquals( info.shortRevision, None, "Git should have a short revision" )

	def testScmGitOneLineCommitMessage( self ):
		self._initialize( self.GIT_EXAMPLE, revision = "a01b256f848e362efbf9f65cc4118c6ebe521539" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )
		self.assertEquals( len( info.commitMessage.split( '\n' ) ), 1, "Commit message is not properly aligned" )
		self.assertTrue( isinstance( info.commitMessage, basestring ) )

	def testScmGitMultiLineCommitMessage( self ):
		self._initialize( self.GIT_EXAMPLE, revision = "f4ac3b0233ed1622e75643882c073d26ee5971d5" )

		info = self.project.getScm().getRevisionInfo()
		self._validateRevisionInfoContent( info )
		self.assertEquals( len( info.commitMessage.split( '\n' ) ), 6, "Commit message is not properly aligned" )
		self.assertTrue( isinstance( info.commitMessage, basestring ) )

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


if __name__ == "__main__":
	unittest.main()
