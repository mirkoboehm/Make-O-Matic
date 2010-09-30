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

CMakeSearchPaths = [
				"C:\Program Files\CMake 2.8\bin",
				"C:\Program Files\CMake 2.6\bin"
]

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

	def __init__( self, name = None, inSourceBuild = False ):
		MakefileGeneratorBuilder.__init__( self, name )
		# Use the Plugin support for finding the CMake command
		makeCommand = self.getCommand()
		self._setCommand( 'cmake', CMakeSearchPaths )
		self._setMakefileGeneratorCommand( self.getCommand() )
		self._setCommand( makeCommand )
		self.setInSourceBuild( inSourceBuild )
		self._setOutOfSourceBuildSupported( True )
		self.setCMakeVariables( [] )

	def setCMakeVariables( self, options ):
		self.__options = options

	def getCMakeVariables( self ):
		return self.__options

	def addCMakeVariable( self, option ):
		self.getCMakeVariables().append( option )

	def createConfigureActions( self ):
		configuration = self.getInstructions()
		self.addCMakeVariable( CMakeVariable( 'CMAKE_INSTALL_PREFIX', configuration.getTargetDir() ) )
		arguments = []
		for variable in self.getCMakeVariables():
			arguments.append( '-D{0}'.format( variable ) )
		arguments.append( configuration.getProject().getSourceDir() )
		self._setMakefileGeneratorArguments( arguments )
		MakefileGeneratorBuilder.createConfigureActions( self )
