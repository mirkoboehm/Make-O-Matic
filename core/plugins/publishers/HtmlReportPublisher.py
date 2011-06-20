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

from core.actions.filesystem.CopyActionBase import CopyActionBase
from core.helpers.GlobalMApp import mApp
from core.helpers.PathResolver import PathResolver
from core.helpers.XmlReport import InstructionsXmlReport
from core.helpers.XmlReportConverter import XmlReportConverter
from core.plugins.publishers.Publisher import Publisher
import codecs
import os.path
import shutil

class HtmlReportPublisher( Publisher ):

	def __init__( self, uploaderAction = None, name = None ):
		super( HtmlReportPublisher, self ).__init__( name )

		assert isinstance( uploaderAction, CopyActionBase )
		self.__uploaderAction = uploaderAction

	def preFlightCheck( self ):
		super( HtmlReportPublisher, self ).preFlightCheck()

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
		html = converter.convertToHtml( enableCrossLinking = True )

		# write file
		filePath = os.path.join( self.getSourceLocation(), "index.html" )
		f = codecs.open( filePath, 'w', encoding = "utf-8" )
		f.write( html )
		f.close()

		# temporary: also write report
		filePath = os.path.join( self.getSourceLocation(), "build-report.xml" )
		f = codecs.open( filePath, 'w', encoding = "utf-8" )
		f.write( report.getReport() )
		f.close()

		self._upload()

	def _upload( self ):
		uploaderAction = self.__uploaderAction
		if not uploaderAction:
			return

		uploaderAction.setSourcePath( self.getSourceLocation() )
		uploaderAction.setDestinationPath( PathResolver( self._getFullUploadLocation ) )
		mApp().debugN( self, 5, "Uploading report to {0}".format( uploaderAction.getDestinationPath() ) )

		rc = uploaderAction.executeAction()
		if rc != 0:
			mApp().debug( self, "Uploading failed:", uploaderAction.getStdErr() )
