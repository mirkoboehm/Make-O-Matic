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
from core.modules.configurations.Builder import Builder
from core.executomat.ShellCommandAction import ShellCommandAction
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from core.helpers.RunCommand import RunCommand
from core.Exceptions import ConfigurationError

# FIXME add variants of make? That provide make tool name, version check command, ...? 
class MakeBasedBuilder( Builder ):
	'''MakeBasedBuilder implements a base class for builders that implement variants of a build process that uses the make tools.'''

	def __init__( self, name ):
		Builder.__init__( self, name )
		self.setMakeOptions( None )
		self.setMakeInstallOptions( None )
		self.setMakeToolName( mApp().getSettings().get( Settings.MakeBuilderMakeTool ) )

	def setMakeOptions( self, options ):
		self.__makeOptions = options

	def getMakeOptions( self ):
		return self.__makeOptions

	def setMakeInstallOptions( self, options ):
		self.__makeInstallOptions = options

	def getMakeInstallOptions( self ):
		return self.__makeInstallOptions

	def preFlightCheck( self ):
		runner = RunCommand( '{0} {1}'.format( self.getMakeToolName(), '--version' ) )
		runner.run()
		if runner.getReturnCode() != 0:
			raise ConfigurationError( 'MakeBasedBuilder: make tool "{0}" not found.'.format( self.getMakeToolName() ) )
		else:
			lines = runner.getStdOut().decode().split( '\n' )
			description = lines[0].rstrip()
			mApp().debugN( self, 4, 'make tool found: "{0}"'.format( description ) )

	def setMakeToolName( self, tool ):
		check_for_nonempty_string_or_none( tool, 'The make tool name must be a non-empty string, or None.' )
		self.__makeTool = tool

	def getMakeToolName( self ):
		return self.__makeTool

	def _getBuildDir( self ):
		configuration = self.getInstructions()
		return configuration.getBuildDir()

	def createConfMakeActions( self ):
		options = self.getMakeOptions() or ''
		cmd = ' '.join( [ self.getMakeToolName(), options ] )
		action = ShellCommandAction( cmd )
		action.setWorkingDirectory( self._getBuildDir() )
		step = self.getInstructions().getStep( 'conf-make' )
		step.addMainAction( action )

	def createConfMakeInstallActions( self ):
		cmd = ' '.join( [
			self.getMakeToolName(),
			self.getMakeInstallOptions() or '',
			mApp().getSettings().get( Settings.MakeBuilderInstallTarget ) ] )
		action = ShellCommandAction( cmd )
		action.setWorkingDirectory( self._getBuildDir() )
		step = self.getInstructions().getStep( 'conf-make-install' )
		step.addMainAction( action )

