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
from core.helpers.TypeCheckers import check_for_path
from core.executomat.ShellCommandAction import ShellCommandAction

class DoxygenGenerator( Plugin ):

	def __init__( self, name = None ):
		'''Constructor'''
		Plugin.__init__( self, name )
		self._setCommand( "doxygen" )
		self.__doxygenFile = None
		self.__docsDir = 'docs'

	def setDoxygenFile( self, doxygenFile ):
		self.__doxygenFile = doxygenFile

	def getDoxygenFile( self ):
		return self.__doxygenFile

	def setup( self ):
		check_for_path( self.getDoxygenFile(), 'The doxygen configuration file name needs to be a nonempty string!' )
		step = self.getInstructions().getStep( 'project-create-docs' )
		cmd = [ self.getCommand(), str( self.getDoxygenFile() ) ]
		doxygenCall = ShellCommandAction( cmd )
		doxygenCall.setWorkingDirectory( self.getInstructions().getScm().getSrcDir() )
		step.addMainAction( doxygenCall )

