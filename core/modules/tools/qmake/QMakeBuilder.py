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

class QMakeBuilder( MakeBasedBuilder ):
	'''QMakeBuilder generates the actions to build a project with qmake.'''

	def __init__( self, name = None ):
		MakeBasedBuilder.__init__( self, name )
		self.__makefileGeneratorCommand = 'qmake'
		self.setInSourceBuild( True )

	def _setMakefileGeneratorCommand( self, makefileGeneratorCommand ):
		self.__makefileGeneratorCommand = makefileGeneratorCommand

	def getMakefileGeneratorCommand( self ):
		return self.__makefileGeneratorCommand

	def setInSourceBuild( self, onOff ):
		self.__inSourceBuild = onOff

	def getInSourceBuild( self ):
		return self.__inSourceBuild

	def preFlightCheck( self ):
		RunCommand( [ self.getMakefileGeneratorCommand() ] ).checkVersion( expectedReturnCode = 154 )
		MakeBasedBuilder.preFlightCheck( self )

	def createPrepareSourceDirActions( self ):
		if not self.getInSourceBuild():
			raise NotImplementedError( 'Sorry, out-of-source builds with QMake are not implemented.' )

	def createConfigureActions( self ):
		configuration = self.getInstructions()
		action = ShellCommandAction( [ self.getMakefileGeneratorCommand() ] )
		action.setWorkingDirectory( configuration.getSourceDir() )
		step = self.getInstructions().getStep( 'conf-configure' )
		step.addMainAction( action )
