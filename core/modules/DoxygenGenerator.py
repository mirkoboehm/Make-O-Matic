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
from core.Plugin import Plugin
from core.helpers.RunCommand import RunCommand
from core.Exceptions import ConfigurationError
from core.helpers.TypeCheckers import check_for_nonempty_string, check_for_path
from core.executomat.ShellCommandAction import ShellCommandAction
from core.helpers.GlobalMApp import mApp

class DoxygenGenerator( Plugin ):

	def __init__( self, name = None ):
		'''Constructor'''
		Plugin.__init__( self, name )
		self.__doxygenPath = 'doxygen'
		self.__doxygenFile = None
		self.__docsDir = 'docs'

	def setDoxygenPath( self, doxygenPath ):
		check_for_nonempty_string( doxygenPath, 'The doxygen path must be the full path to the doxygen program!' )
		self.__doxygenPath = doxygenPath

	def getDoxygenPath( self ):
		return self.__doxygenPath

	def setDoxygenFile( self, file ):
		self.__doxygenFile = file

	def getDoxygenFile( self ):
		return self.__doxygenFile

	def preFlightCheck( self, instructions ):
		assert instructions
		runner = RunCommand( 'doxygen --version' )
		runner.run()
		if( runner.getReturnCode() != 0 ):
			raise ConfigurationError( "DoxygenGenerator: doxygen not found." )
		else:
			lines = runner.getStdOut().decode().split( '\n' )
			version = lines[0].rstrip()
			mApp().debugN( self, 1, 'doxygen found: "{0}"'.format( version ) )

	def setup( self, instructions ):
		check_for_path( self.getDoxygenFile(), 'The doxygen configuration file name needs to be a nonempty string!' )
		step = instructions.getExecutomat().getStep( 'project-create-docs' )
		doxygenCall = ShellCommandAction( '{0} {1}'
			.format ( self.getDoxygenPath(), self.getDoxygenFile() ) )
		doxygenCall.setWorkingDirectory( instructions.getScm().getSrcDir() )
		step.addMainAction( doxygenCall )

