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

from core.Plugin import Plugin
from core.modules.reporters.XmlReport import XmlReport
import os.path
from core.Exceptions import ConfigurationError

class XmlReportGenerator( Plugin ):

	def __init__( self ):
		Plugin.__init__( self, self.__class__.__name__ )

		self.__fileHandle = None
		self.__reportFile = None

	def shutDown( self ):
		report = XmlReport( self.getInstructions() )
		report.prepare()

		self._openReportFile()
		self._writeReport( report )
		self._saveReportFile()

	def getReportFile( self ):
		return self.__reportFile

	def _openReportFile( self ):
		baseDirectory = self.getInstructions().getBaseDir()
		reportFileName = "{0}-report.xml".format( self.getInstructions().getTagName() )

		if not os.path.isdir( baseDirectory ):
			raise ConfigurationError( 'Log directory at "{0}" does not exist.'.format( str( baseDirectory ) ) )

		try:
			self.__reportFile = baseDirectory + os.sep + reportFileName
			self.__fileHandle = open( self.__reportFile, 'w' )
		except:
			raise ConfigurationError( 'Cannot open log file at "{0}"'.format( reportFileName ) )

	def _writeReport( self, report ):
		if self.__fileHandle and report:
			self.__fileHandle.write( report.getReport() )

	def _saveReportFile( self ):
		if self.__fileHandle:
			self.__fileHandle.close()
