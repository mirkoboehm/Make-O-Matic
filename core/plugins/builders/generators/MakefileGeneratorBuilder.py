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

from core.plugins.builders.MakeBasedBuilder import MakeBasedBuilder
from core.actions.ShellCommandAction import ShellCommandAction

class MakefileGeneratorBuilder( MakeBasedBuilder ):
	'''MakefileGeneratorBuilder generates the actions to build a project from a tool
	 that generates makefiles.'''

	def __init__( self, name = None ):
		MakeBasedBuilder.__init__( self, name )
		self._setInSourceBuildSupported( True )
		self._setOutOfSourceBuildSupported( True )
		self.setInSourceBuild( False )

	def createConfigureActions( self ):
		if not self.getCommand():
			raise NotImplementedError()
		command = [ self.getCommand() ]
		command.extend( self.getCommandArguments() )
		action = ShellCommandAction( command )
		action.setWorkingDirectory( self._getBuildDir() )
		step = self.getInstructions().getStep( 'conf-configure' )
		step.addMainAction( action )
