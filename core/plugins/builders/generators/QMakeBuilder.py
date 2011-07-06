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

from core.plugins.builders.generators.MakefileGeneratorBuilder import MakefileGeneratorBuilder
import os
from core.helpers.GlobalMApp import mApp
from core.helpers.TypeCheckers import check_for_path

class QMakeBuilder( MakefileGeneratorBuilder ):
	'''QMakeBuilder generates the actions to build a project with qmake.'''

	def __init__( self, name = None, projectFile = None ):
		MakefileGeneratorBuilder.__init__( self, name )
		self.enableInstallation( False )
		self.__projectFilePath = projectFile
		self._setCommand( "qmake" )
		self.setQMakeArguments( [] )

	def setQMakeArguments( self, args ):
		self.__qmakeArguments = args

	def getQMakeArguments( self ):
		return self.__qmakeArguments

	def enableInstallation( self, onoff ):
		self.__install = onoff

	def installEnabled( self ):
		return self.__install

	def setProjectFilePath( self, projectFilePath ):
		"""Set the project file path for this builder

		\param projectFilePath Likely a path in the form of /path/to/source/project.pro"""

		check_for_path( projectFilePath, "Project file property must be a valid path" )
		self.__projectFilePath = projectFilePath

	def getProjectFilePath( self ):
		return self.__projectFilePath

	def createConfigureActions( self ):
		configuration = self.getInstructions()
		project = configuration.getProject()
		sourceDirectory = project.getSourceDir()
		projectFileName = self.getProjectFilePath()
		if not projectFileName:
			# use the project name, that is Make-O-Matic's convention
			name = project.getName()
		if self.getInSourceBuild():
			sourceDirectory = configuration.getBuildDir()
		if configuration.getSourcePrefix():
			sourceSubDir = os.path.join( sourceDirectory, configuration.getSourcePrefix() )
			# use the folder name, as that is the convention with QMake
			name = os.path.basename( sourceSubDir )
			if not self.getInSourceBuild():
				sourceDirectory = sourceSubDir
		projectFileName = "{0}.pro".format( name )
		# set commands:
		proFile = os.path.join( sourceDirectory, projectFileName )
		self._setCommandArguments( [ proFile ] + self.getQMakeArguments() )

		super( QMakeBuilder, self ).createConfigureActions()

	def createConfMakeInstallActions( self ):
		# Stupidly, QMake doesn't have a standard way of installing to a prefix so just disable this
		if self.installEnabled():
			super( QMakeBuilder, self ).createConfMakeInstallActions()
		else:
			mApp().debugN( self, 3, 'Installation is not implemented by the project, not generating any actions.' )
			pass
