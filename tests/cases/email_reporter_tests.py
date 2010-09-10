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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import unittest
from core.modules.reporters.EmailReporter import EmailReporter
from tests.helpers.MomBuildMockupTestCase import MomBuildMockupTestCase

class EmailReporterTest( MomBuildMockupTestCase ):

	def testEmailReporterPlugin( self ):
		# TODO: Modify email recipients list for testing

		# add EmailReporter plugin
		self.build.addPlugin( EmailReporter() )

		self.build.runPreFlightChecks()
		self.build.runSetups()
		self.build.buildAndReturn()

if __name__ == "__main__":
	unittest.main()
