# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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
import os
from core.helpers.EnvironmentSaver import EnvironmentSaver

class EnvironmentSaverTest( unittest.TestCase ):

	def testSetVariable( self ):
		testVariable = 'TEST_ENVIRONMENT_VARIABLE'
		testContent = 'TEST_CONTENT'
		with EnvironmentSaver():
			os.environ[testVariable] = testContent
			self.assertEqual( os.environ[ testVariable], testContent )
		self.assertTrue( testVariable not in os.environ )

	def testChangeDirectory( self ):
		oldCwd = os.getcwd()
		tmpDir = '/' #FIXME does this work on Windows?
		with EnvironmentSaver():
			os.chdir( tmpDir )
			self.assertEqual( os.getcwd(), tmpDir )
		self.assertEqual( os.getcwd(), oldCwd )

if __name__ == "__main__":
	unittest.main()
