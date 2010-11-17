# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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

from core.plugins.testers.TestProvider import TestProvider
from core.plugins.builders.generators.CMakeBuilder import CMakeSearchPaths
from core.helpers.GlobalMApp import mApp
import re

class CTest( TestProvider ):

	def __init__( self, name = None ):
		TestProvider.__init__( self, name )
		self._setCommand( "ctest", CMakeSearchPaths )
		self._setCommandArguments( ["--verbose"] )

	def saveReport( self ):
		mApp().debug( self, "Saving unit test report" )

		stdout = self.getAction()._getRunner().getStdOut()
		if not stdout:
			return

		rx = re.compile( "^(\d+\%) tests passed, (\d+) tests failed out of (\d+).*", re.MULTILINE | re.DOTALL )
		matches = rx.search( stdout )
		if matches:
			report = "{0} tests passed".format( matches.groups()[0] )
			failed = int ( matches.groups()[1] )
			total = int( matches.groups()[2] )
			self._setReport( report )
			self._setScore( total - failed, total )
