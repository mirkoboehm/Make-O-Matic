# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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

from mom.plugins.testers.QTest import QTest
from mom.tests.helpers.MomTestCase import MomTestCase
import unittest

class QTestTests( MomTestCase ):

	def testQTestParser( self ):
		output = '''\
make[2]: Entering directory `/folder'
./TestProgram
********* Start testing of TestProgram *********
Config: Using QTest library 4.7.1, Qt 4.7.1
PASS   : TestProgram::initTestCase()
PASS   : TestProgram::test1()
PASS   : TestProgram::test2()
PASS   : TestProgram::test3()
PASS   : TestProgram::test4()
PASS   : TestProgram::test5()
PASS   : TestProgram::test6()
PASS   : TestProgram::test7()
PASS   : TestProgram::test8()
PASS   : TestProgram::cleanupTestCase()
Totals: 10 passed, 0 failed, 0 skipped
********* Finished testing of TestProgram *********
make[2]: Leaving directory `/folder'
'''
		parser = QTest()
		totalPassed, totalFailed, totalSkipped = parser._parseReport( output )
		self.assertEquals( totalPassed, 10 )
		self.assertEquals( totalFailed, 0 )
		self.assertEquals( totalSkipped, 0 )

if __name__ == "__main__":
	unittest.main()
