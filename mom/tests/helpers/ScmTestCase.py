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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from mom.tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase

class ScmTestCase( MomBuildMockupTestCase ):

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
		self.assertTrue( info.isValid(), "Revision information not valid" )
