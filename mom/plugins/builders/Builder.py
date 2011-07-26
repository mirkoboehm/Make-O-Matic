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
from mom.core.Plugin import Plugin
from mom.core.actions.filesystem.DirectoryTreeCopyAction import DirectoryTreeCopyAction
import os

class Builder( Plugin ):
	'''A Builder creates the actions to build a configuration for a project.
	It needs to be assigned to a configuration.'''

	def __init__( self, name = None ):
		Plugin.__init__( self, name )
		self.__inSourceBuild = False
		self.__inSourceBuildSupported = False
		self.__outOfSourceBuildSupported = False

	def setInSourceBuild( self, inSourceBuild ):
		self.__inSourceBuild = inSourceBuild

	def getInSourceBuild( self ):
		return self.__inSourceBuild

	def _setInSourceBuildSupported( self, inSourceBuildSupported ):
		self.__inSourceBuildSupported = inSourceBuildSupported

	def _setOutOfSourceBuildSupported( self, outOfSourceBuildSupported ):
		self.__outOfSourceBuildSupported = outOfSourceBuildSupported

	def createPrepareSourceDirActions( self ):
		if self.getInSourceBuild():
			if not self.__inSourceBuildSupported:
				raise NotImplementedError( 'In-source builds are not supported by this Builder.' )
			# If we're doing an in-source build, copy the tree to the build directory
			configuration = self.getInstructions()
			source = os.path.join( configuration.getProject().getSourceDir(), configuration.getSourcePrefix() )
			build = configuration.getBuildDir()
			ignore = ['.svn/', '.git/']
			step = self.getInstructions().getStep( 'export-sources' )
			step.addMainAction( DirectoryTreeCopyAction( source, build, ignore ) )
		else:
			if not self.__outOfSourceBuildSupported:
				raise NotImplementedError( 'Out-of-source builds are not supported by this Builder.' )

	def createConfigureActions( self ):
		raise NotImplementedError()

	def createConfMakeActions( self ):
		raise NotImplementedError()

	def createConfMakeInstallActions( self ):
		raise NotImplementedError()

	def setup( self ):
		self.createPrepareSourceDirActions()
		self.createConfigureActions()
		self.createConfMakeActions()
		self.createConfMakeInstallActions()
