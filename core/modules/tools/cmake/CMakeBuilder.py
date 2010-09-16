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
from core.modules.configurations.MakeBasedBuilder import MakeBasedBuilder
from core.executomat.ShellCommandAction import ShellCommandAction
from core.helpers.RunCommand import RunCommand

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

class CMakeBuilder( MakeBasedBuilder ):
	'''CMakeBuilder generates the actions to build a project with cmake.'''

	def __init__( self, name = None ):
		MakeBasedBuilder.__init__( self, name )
		self.__cmakeCommand = 'cmake'
		self.setInSourceBuild( False )
		self.setCMakeVariables( [] )

	def _setCMakeCommand( self, cmakeCommand ):
		self.__cmakeCommand = cmakeCommand

	def getCMakeCommand( self ):
		return self.__cmakeCommand

	def preFlightCheck( self ):
		RunCommand( [ self.getCMakeCommand() ] ).checkVersion()
		MakeBasedBuilder.preFlightCheck( self )

	def setInSourceBuild( self, onOff ):
		self.__inSourceBuild = onOff

	def getInSourceBuild( self ):
		return self.__inSourceBuild

	def setCMakeVariables( self, options ):
		self.__options = options

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
		self.addCMakeVariable( CMakeVariable( 'CMAKE_INSTALL_PREFIX', configuration.getTargetDir() ) )
		cmd = [ self.getCMakeCommand() ]
		for variable in self.getCMakeVariables():
			cmd.append( '-D{0}'.format( variable ) )
		cmd.append( srcDir )
		action = ShellCommandAction( cmd )
		action.setWorkingDirectory( configuration.getBuildDir() )
		step = self.getInstructions().getStep( 'conf-configure' )
		step.addMainAction( action )
