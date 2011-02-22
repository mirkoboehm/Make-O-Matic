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
from core.plugins.builders.Builder import Builder
from core.actions.ShellCommandAction import ShellCommandAction
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
import multiprocessing
from core.plugins.builders import maketools
from core.plugins.builders.maketools import getMakeTool

class MakeBasedBuilder( Builder ):
	'''MakeBasedBuilder implements a base class for builders that implement variants of a build process that uses the make tools.'''

	def __init__( self, name = None ):
		Builder.__init__( self, name )
		self.__makeTool = None

	def preFlightCheck( self ):
		self.__makeTool = maketools.getMakeTool()
		if not self.getCommand():
			self._setCommand( self.__makeTool.getCommand() )
		if not self.getCommandSearchPaths():
			self._setCommandSearchPaths( self.__makeTool.getCommandSearchPaths() )
		self.getMakeTool().checkVersion()

	def _getBuildDir( self ):
		return self.getInstructions().getBuildDir()

	def getMakeTool( self ):
		return self.__makeTool

	def createConfMakeActions( self ):
		tool = self.getMakeTool()
		# The make tool is discovered during pre-flight check. It is not set in query and describe mode, so don't assume it is. 
		if tool:
			tool.setJobs( multiprocessing.cpu_count() )
			command = [ tool.getCommand() ]
			command.extend( tool.getArguments() )
			action = ShellCommandAction( command, searchPaths = getMakeTool().getCommandSearchPaths() )
			action.setWorkingDirectory( self._getBuildDir() )
			step = self.getInstructions().getStep( 'build' )
			step.addMainAction( action )

	def createConfMakeInstallActions( self ):
		tool = self.getMakeTool()
		# The make tool is discovered during pre-flight check. It is not set in query and describe mode, so don't assume it is. 
		if tool:
			# There's often problems with more than one make install job and it's I/O bound anyway
			tool.setJobs( 1 )
			command = [ tool.getCommand() ]
			command.append( mApp().getSettings().get( Settings.MakeBuilderInstallTarget ) )
			action = ShellCommandAction( command, searchPaths = getMakeTool().getCommandSearchPaths() )
			action.setWorkingDirectory( self._getBuildDir() )
			step = self.getInstructions().getStep( 'install' )
			step.addMainAction( action )
