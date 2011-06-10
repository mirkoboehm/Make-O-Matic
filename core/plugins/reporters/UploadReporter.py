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

from core.Plugin import Plugin
from core.helpers.GlobalMApp import mApp
import os.path
import shutil
from core.helpers.XmlReport import InstructionsXmlReport
from core.helpers.XmlReportConverter import XmlReportConverter
import codecs

class UploadReporter( Plugin ):

	def __init__( self, name = None ):
		super( UploadReporter, self ).__init__( name )

	def preFlightCheck( self ):
		super( UploadReporter, self ).preFlightCheck()

	def getSourceLocation( self ):
		baseDir = mApp().getBaseDir()
		return os.path.join( baseDir, "upload" )

	def _copyDirectory( self, sourceDirectory, relativeTargetDirectory ):
		targetDirectory = os.path.join( self.getSourceLocation(), relativeTargetDirectory )

		mApp().debugN( self, 5, "Copying {0} to {1}".format( sourceDirectory, targetDirectory ) )
		shutil.copytree( sourceDirectory, targetDirectory )

	def _cloneDirectories( self ):
		self._copyDirectory( mApp().getLogDir(), "log" )
		self._copyDirectory( mApp().getPackagesDir(), "packages" )

	def report( self ):
		self._cloneDirectories()

		report = InstructionsXmlReport( mApp() )
		converter = XmlReportConverter( report )
		html = converter.convertToHtml( True )
		filePath = os.path.join( self.getSourceLocation(), "index.html" )

		# write file
		f = codecs.open( filePath, 'w', encoding = "utf-8" )
		f.write( html )
		f.close()
