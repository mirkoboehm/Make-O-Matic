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
from core.actions.ShellCommandAction import ShellCommandAction

class PackageProvider( Plugin ):

	def __init__( self, name = None ):
		Plugin.__init__( self, name )

	def makePackageStep( self ):
		"""Create package for the project."""
		if self.getCommandArguments() == None:
			raise NotImplementedError()
		step = self.getInstructions().getStep( 'create-packages' )
		command = [ self.getCommand() ]
		command.extend( self.getCommandArguments() )
		makePackage = ShellCommandAction( command, searchPaths = self.getCommandSearchPaths() )
		makePackage.setWorkingDirectory( self.getInstructions().getBuildDir() )
		step.addMainAction( makePackage )
		return makePackage

	def setup( self ):
		"""Setup is called after the package steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makePackageStep()

	def getRelativeLinkTarget( self ):
		return ( self.getInstructions().getPackagesDir(), "Get packages for this configuration" )
