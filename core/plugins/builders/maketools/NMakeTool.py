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
from core.plugins.builders.maketools.MakeTool import MakeTool
import sys

class NMakeTool( MakeTool ):
	'''NMakeTool implements a class for the Microsoft NMake makefile tool.'''

	def __init__( self ):
		MakeTool.__init__( self )
		searchPaths = []
		if sys.platform == "win32":
			from core.helpers.RegistryHelper import getPathsFromRegistry
			keys = []
			keys += "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\10.0\InstallDir"
			keys += "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\9.0\InstallDir"
			keys += "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VCExpress\9.0\InstallDir"
			keys += "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\8.0\InstallDir"
			searchPaths += getPathsFromRegistry( keys, "..\..\VC\bin" )
		self._setCommand( 'nmake', searchPaths )
		self._setVersionParameter( '/?' )

	def getArguments( self ):
		return [ '/nologo' ]
