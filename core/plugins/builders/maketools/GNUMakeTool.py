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

class GNUMakeTool( MakeTool ):
	'''GNUMakeTool implements a class for a the GNU Make makefile tool.'''

	def __init__( self ):
		MakeTool.__init__( self )
		searchPaths = []
		if sys.platform == "win32":
			from core.helpers.RegistryHelper import getPathsFromRegistry
			keys = [ "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MinGW\InstallLocation",
				"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MSYS-1.0_is1\Inno Setup: App Path" ]
			searchPaths += getPathsFromRegistry( keys, "bin" )
		self._setCommand( 'make' )

	def getArguments( self ):
		return [ '-j{0}'.format( self._getJobs() )  ]
