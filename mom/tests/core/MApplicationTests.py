# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko.boehm@kdab.com>
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

from mom.core.Exceptions import MomError
from mom.tests.helpers.CrashMePlugin import CrashMePlugin
from mom.tests.helpers.MomTestCase import MomTestCase
from mom.tests.helpers.TestUtils import replace_bound_method
import unittest
from mom.core.MApplication import MApplication
from mom.core.helpers.GlobalMApp import mApp
from mom.core.loggers.ConsoleLogger import ConsoleLogger

class MApplicationTests( MomTestCase ):

	def testExceptionIntrospection( self ):
		build = self.build

		plugin = CrashMePlugin()
		build.addPlugin( plugin )

		def setup_new( self ):
			raise MomError( 'Test ' )

		replace_bound_method( plugin, plugin.setup, setup_new )
		build.buildAndReturn()
		self.assertTrue( build.getException()[0].getPhase() == MApplication.Phase.Setup )


if __name__ == "__main__":
	unittest.main()
