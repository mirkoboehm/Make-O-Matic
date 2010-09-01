# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
# 
# make-o-matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# make-o-matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from core.modules.configurations.MakeBasedBuilder import MakeBasedBuilder
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.executomat.ShellCommandAction import ShellCommandAction

class CMakeVariable( object ):
	def __init__( self, name, value, type = None ):
		self.setName( name )
		self.setValue( value )
		self.setType( type )

	def setName( self, name ):
		self.__name = name

	def getName( self ):
		return self.__name

	def setType( self, type ):
		self.__type = type

	def getType( self ):
		return self.__type

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

class CMakeBuilder( MakeBasedBuilder ):
	'''CMakeBuilder generates the actions to build a project with cmake.'''

	def __init__( self, name = None ):
		MakeBasedBuilder.__init__( self, name )
		self.setCMakeToolName( mApp().getSettings().get( Settings.CMakeBuilderTool ) )
		self.setInSourceBuild( False )
		self.setCMakeVariables( [] )

	def setCMakeToolName( self, tool ):
		self.__cmakeTool = tool

	def getCMakeToolName( self ):
		return self.__cmakeTool

	def setInSourceBuild( self, onOff ):
		self.__inSourceBuild = onOff

	def getInSourceBuild( self ):
		return self.__inSourceBuild

	def setCMakeVariables( self, options ):
		self.__options = []

	def getCMakeVariables( self ):
		return self.__options

	def addCMakeVariable( self, option ):
		self.getCMakeVariables().append( option )

	def createPrepareSourceDirActions( self ):
		if self.getInSourceBuild():
			raise NotImplementedError( 'Sorry, in-source builds with CMake are not implemented.' )

	def createConfigureActions( self ):
		configuration = self.getInstructions()
		project = configuration.getProject()
		srcDir = project.getSourceDir()
		self.addCMakeVariable( CMakeVariable( 'CMAKE_INSTALL_PREFIX', configuration.getFolderManager().getTargetDir() ) )
		variables = []
		for variable in self.getCMakeVariables():
			variables.append( '-D{0}'.format( variable ) )
		cmd = '{0} {1} {2}'.format( self.getCMakeToolName(), ' '.join( variables ), srcDir )
		action = ShellCommandAction( cmd )
		action.setWorkingDirectory( configuration.getFolderManager().getBuildDir() )
		step = self.getInstructions().getExecutomat().getStep( 'conf-configure' )
		step.addMainAction( action )
