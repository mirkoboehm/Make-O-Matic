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

from core.plugins.builders.generators.MakefileGeneratorBuilder import MakefileGeneratorBuilder
import sys
from core.helpers.GlobalMApp import mApp
from core.plugins.builders.maketools.NMakeTool import NMakeTool
from core.plugins.builders.maketools import JomTool
from core.plugins.builders.maketools import getMakeTools
from core.plugins.builders.maketools.MingwMakeTool import MingwMakeTool
from core.Exceptions import ConfigurationError
import os

def getCMakeSearchPaths():
	searchPaths = []
	if sys.platform == "win32":
		from core.helpers.RegistryHelper import getPathsFromRegistry
		registryKeys = [ "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\CMake\\UninstallString" ]
		relativePath = "../bin"
		searchPaths += getPathsFromRegistry( registryKeys, relativePath )
	return searchPaths

class CMakeVariable( object ):
	def __init__( self, name, value, typeString = None ):
		self.setName( name )
		self.setValue( value )
		self.setType( typeString )

	def setName( self, name ):
		self.__name = name

	def getName( self ):
		return self.__name

	def setType( self, typeString ):
		self.__typeString = typeString

	def getType( self ):
		return self.__typeString

	def setValue( self, value ):
		self.__value = value

	def getValue( self ):
		return self.__value

	def __str__( self ):
		text = '{0}{1}{2}={3}'.format(
			self.getName(),
			':' if self.getType() else '',
			self.getType() if self.getType() else '',
			self.getValue() )
		return text

class CMakeBuilder( MakefileGeneratorBuilder ):
	'''CMakeBuilder generates the actions to build a project with cmake.'''

	def getCMakeGeneratorSwitch( self ):
		"""\see http://cmake.org/Wiki/CMake_Generator_Specific_Information"""

		if not self.getMakeTool():
			return None

		# do not escape or quote here, it does not work for some reason
		jom = False
		for MakeTool in getMakeTools():
			if MakeTool == JomTool:
				jom = True
			else:
				tool = MakeTool()
				try:
					tool.resolveCommand()
				except ConfigurationError:
					pass
				else:
					if MakeTool == NMakeTool:
						if jom:
							return '-GNMake Makefiles JOM'
						else:
							return '-GNMake Makefiles'
					elif MakeTool == MingwMakeTool:
						return '-GMinGW Makefiles'

		return None

	def __init__( self, name = None, inSourceBuild = False ):
		MakefileGeneratorBuilder.__init__( self, name )
		self._setCommand( 'cmake' )
		self._setCommandSearchPaths( getCMakeSearchPaths() )
		self.setInSourceBuild( inSourceBuild )
		self._setOutOfSourceBuildSupported( True )
		self.__cmakeVariables = []

	def setCMakeVariables( self, variables ):
		self.__cmakeVariables = variables

	def getCMakeVariables( self ):
		return self.__cmakeVariables

	def addCMakeVariable( self, variable ):
		self.getCMakeVariables().append( variable )

	def createConfigureActions( self ):
		configuration = self.getInstructions()
		self.addCMakeVariable( CMakeVariable( 'CMAKE_INSTALL_PREFIX', configuration.getTargetDir() ) )
		arguments = []

		generatorSwitch = self.getCMakeGeneratorSwitch()
		if generatorSwitch:
			mApp().debugN( self, 5, 'adding cmake generator switch: {0}'.format( generatorSwitch ) )
			arguments.append( generatorSwitch )

		for variable in self.getCMakeVariables():
			arguments.append( '-D{0}'.format( variable ) )

		sourceDir = configuration.getProject().getSourceDir()
		if configuration.getSourcePrefix():
			sourceDir = os.path.join( sourceDir, configuration.getSourcePrefix() )
		arguments.append( sourceDir )
		self._setCommandArguments( arguments )
		MakefileGeneratorBuilder.createConfigureActions( self )
