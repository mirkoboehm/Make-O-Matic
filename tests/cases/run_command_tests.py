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
from core.helpers.RunCommand import RunCommand
from core.Exceptions import ConfigurationError
from tests.helpers.MomTestCase import MomTestCase

class RunCommandTests( MomTestCase ):
	# these are not a windows friendly tests, i guess

	def testCheckQMakeVersion( self ):
		# qmake example
		qmakeCommand = RunCommand( [ "qmake" ] )
		self.assertRaises( ConfigurationError, qmakeCommand.checkVersion, expectedReturnCode = 0 ) # qmake returns 154

		version = qmakeCommand.checkVersion( expectedReturnCode = 154 )
		self.assertTrue( "Qmake" in version and "Qt" in version )

	def testCheckCMakeVersion( self ):
		# cmake example
		cmakeCommand = RunCommand( [ "cmake" ] )
		self.assertRaises( ConfigurationError, cmakeCommand.checkVersion, expectedReturnCode = -1 ) # cmake returns 0

		version = cmakeCommand.checkVersion( expectedReturnCode = 0 )
		self.assertTrue( "cmake version" in version )

if __name__ == "__main__":
	unittest.main()