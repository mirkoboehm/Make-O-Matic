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

from mom.core.helpers.XmlReport import InstructionsXmlReport
from mom.core.helpers.XmlReportConverter import XmlReportConverter
from mom.plugins.reporters.Reporter import Reporter

class ConsoleReporter( Reporter ):

	def __init__( self, name = None ):
		Reporter.__init__( self, name )

	def report( self ):
		if self.isReportSent():
			return

		report = InstructionsXmlReport( self.getInstructions() )
		converter = XmlReportConverter( report )

		print( " " )
		print( converter.convertToTextSummary().encode( "utf-8" ) )
		print( converter.convertToText().encode( "utf-8" ) )
		print( " " ) # empty line
		self._setIsReportSent( True )
