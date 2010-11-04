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

from core.Plugin import Plugin
from core.helpers.TypeCheckers import check_for_list_of_strings
from core.actions.ShellCommandAction import ShellCommandAction

class PackageProvider( Plugin ):

	def __init__( self, name = None ):
		Plugin.__init__( self, name )
		self.__packageArguments = None

	def _setPackageArguments( self, packageArguments ):
		check_for_list_of_strings( packageArguments, "The package argument needs to be a list of strings" )
		self.__packageArguments = packageArguments

	def _getPackageArguments( self ):
		return self.__packageArguments

	def makePackageStep( self ):
		"""Create package for the project."""
		if self._getPackageArguments() == None:
			raise NotImplementedError()
		step = self.getInstructions().getStep( 'conf-package' )
		command = [ self.getCommand() ]
		command.extend( self._getPackageArguments() )
		makePackage = ShellCommandAction( command )
		makePackage.setWorkingDirectory( self.getInstructions().getBuildDir() )
		step.addMainAction( makePackage )
		return makePackage

	def setup( self ):
		"""Setup is called after the package steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makePackageStep()
