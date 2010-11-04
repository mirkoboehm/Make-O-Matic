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

from core.Plugin import Plugin
from core.helpers.TypeCheckers import check_for_path, check_for_path_or_none
from core.actions.ShellCommandAction import ShellCommandAction
import sys
import os
from core.actions.filesystem.RmDirAction import RmDirAction
from core.actions.filesystem.MkDirAction import MkDirAction

class DoxygenGenerator( Plugin ):

	def __init__( self, name = None ):
		'''Constructor'''
		Plugin.__init__( self, name )
		searchPaths = []
		if sys.platform == "win32":
			from core.helpers.RegistryHelper import getPathsFromRegistry
			keys = [ "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\doxygen_is1\\Inno Setup: App Path" ]
			searchPaths += getPathsFromRegistry( keys, "bin" )
		self._setCommand( "doxygen", searchPaths )
		self.__doxygenFile = None
		self.setDocsDir( None )

	def setDocsDir( self, dir ):
		check_for_path_or_none( dir , 'The docs directory must be a non-empty string or path!' )
		self.__docsDir = dir

	def getDocsDir( self ):
		return self.__docsDir

	def setDoxygenFile( self, doxygenFile ):
		self.__doxygenFile = doxygenFile

	def getDoxygenFile( self ):
		return self.__doxygenFile

	def setup( self ):
		check_for_path( self.getDoxygenFile(), 'The doxygen configuration file name needs to be a nonempty string!' )
		docsDir = os.path.join( self.getInstructions().getBaseDir(), self.getDocsDir() or self.getInstructions().getDocsDir() )

		# make docs folder
		step = self.getInstructions().getStep( 'project-create-folders' )
		step.addMainAction( MkDirAction( docsDir ) )

		# run doxygen
		step = self.getInstructions().getStep( 'project-create-docs' )
		cmd = [ self.getCommand(), str( self.getDoxygenFile() ) ]
		doxygenCall = ShellCommandAction( cmd )
		doxygenCall.setWorkingDirectory( docsDir )
		step.addMainAction( doxygenCall )

		# cleanup
		step = self.getInstructions().getStep( 'project-cleanup' )
		step.addMainAction( RmDirAction( docsDir ) )

