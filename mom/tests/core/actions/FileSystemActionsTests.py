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

from mom.core.actions.filesystem.RmDirAction import RmDirAction
from mom.tests.helpers.MomTestCase import MomTestCase
import os
import tempfile
import unittest

class FileSystemActionsTests( MomTestCase ):

	def testRmDirActionIfExists( self ):
		path = tempfile.mkdtemp( prefix = 'tmp-mom-' )
		self.assertTrue( os.path.isdir( path ) )

		action = RmDirAction( path )
		rc = action.run()
		self.assertTrue( rc == 0 )
		self.assertTrue( not os.path.isdir( path ) )

	def testRmDirActionIfNotExists( self ):
		path = "/var/tmp/make-o-matic_non_existant_dir/"
		self.assertTrue( not os.path.isdir( path ) )

		action = RmDirAction( path )
		action.run()

if __name__ == "__main__":
	unittest.main()
