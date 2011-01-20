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
from core.helpers.GlobalMApp import mApp
import re
from core.plugins.builders import maketools

class QTest( TestProvider ):

	def __init__( self, name = None ):
		TestProvider.__init__( self, name )
		self.__makeTool = maketools.getMakeTool()
		self._setCommand( self.__makeTool.getCommand() )
		self._setCommandSearchPaths( self.__makeTool.getCommandSearchPaths() )
		self._setCommandArguments( [ 'test' ] )

	def getMakeTool( self ):
		return self.__makeTool

	def preFlightCheck( self ):
		self.getMakeTool().checkVersion()

	def _parseReport( self, report ):
		totalPassed = 0
		totalFailed = 0
		totalSkipped = 0
		for line in report.split( '\n' ):
			match = re.match( '^Totals: (.+) passed, (.+) failed, (.+) skipped$', line )
			if match:
				passed = match.group( 1 )
				totalPassed += int( passed )
				failed = match.group( 2 )
				totalFailed += int( failed )
				skipped = match.group( 3 )
				totalSkipped += int( skipped )
		return totalPassed, totalFailed, totalSkipped

	def saveReport( self ):
		mApp().debugN( self, 3, "Saving unit test report" )

		stdout = self.getAction()._getRunner().getStdOut()
		if not stdout:
			return

		totalPassed, totalFailed, totalSkipped = self._parseReport( stdout )

		report = "{0} tests passed".format( totalPassed )
		if totalSkipped:
			report += " ({0} skipped)".format( totalSkipped )
		total = totalPassed + totalFailed
		self._setReport( report )
		self._setScore( total - totalFailed, total )
