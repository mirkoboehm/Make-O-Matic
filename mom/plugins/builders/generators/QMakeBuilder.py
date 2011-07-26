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

from mom.core.helpers.GlobalMApp import mApp
from mom.core.helpers.TypeCheckers import check_for_nonempty_string_or_none
from mom.plugins.builders.generators.MakefileGeneratorBuilder import MakefileGeneratorBuilder
import os

class QMakeVariable( object ):

	def __init__( self, name, value, type = None ):
		self.setName( name )
		self.setValue( value )
		self.setType( type )

	def setName( self, name ):
		self.__name = name

	def getName( self ):
		return self.__name

	def setValue( self, value ):
		self.__value = value

	def getValue( self ):
		return self.__value

	def setType( self, type ):
		self.__type = type

	def getType( self ):
		return self.__type

	def __str__( self ):
		if self.getType() == None:
			prefix = ''
		elif self.getType() == 'add' :
			prefix = '+'
		else:
			prefix = '-'
		text = '{0}{1}={2}'.format(
			self.getName(),
			prefix,
			str( self.getValue() ) )
		return text

class QMakeBuilder( MakefileGeneratorBuilder ):
	'''QMakeBuilder generates the actions to build a project with qmake.'''

	def __init__( self, name = None, installPrefixVariableName = 'PREFIX' ):
		MakefileGeneratorBuilder.__init__( self, name )

		self.setProjectFileBaseName( None )
		self.enableInstallation( False )
		self._setCommand( "qmake" )
		self.__qmakeVariables = []
		self.setInstallPrefixVariableName( installPrefixVariableName )

	def setQMakeVariables( self, variables ):
		self.__qmakeVariables = variables

	def getQMakeVariables( self ):
		return self.__qmakeVariables

	def addQMakeVariable( self, variable ):
		self.getQMakeVariables().append( variable )

	def enableInstallation( self, onoff ):
		self.__install = onoff

	def installEnabled( self ):
		return self.__install

	def setInstallPrefixVariableName( self, prefix ):
		self.__installPrefixVariableName = prefix

	def getInstllPrefixVariableName( self ):
		return self.__installPrefixVariableName

	def setProjectFileBaseName( self, projectFileBaseName ):
		"""Set the project file base name for this builder

		\param projectFileBaseName 'project' in a path like /path/to/source/project.pro"""

		check_for_nonempty_string_or_none( projectFileBaseName, "Project file base name must be a valid string" )
		self.__projectFileBaseName = projectFileBaseName

	def getProjectFileBaseName( self ):
		return self.__projectFileBaseName

	def getProjectFilePath( self ):
		"""Dynamically get the full project file path of this builder

		When trying to build a special subfolder of a project this will try to use the subfolder's name for the project file
		(e.g. source prefix: subproject/ => return "/source/subproject/subproject.pro"

		\note If self.getProjectFileBaseName() is set this will be used as a overwrite.
		(e.g. self.setProjectFileBaseName("specialproject") => return "/source/subproject/specialproject.pro")

		\return Path to project file, e.g. /path/to/source/project.pro"""

		configuration = self.getInstructions()
		project = configuration.getProject()
		sourceDirectory = project.getSourceDir()

		# use the specified project file name, fall back to project name if empty
		baseName = self.getProjectFileBaseName() or project.getName()

		# overwrite source directory when using the source copy in the build directory
		if self.getInSourceBuild():
			sourceDirectory = configuration.getBuildDir()

		# append source prefix if set
		if configuration.getSourcePrefix():
			sourceSubDir = os.path.join( sourceDirectory, configuration.getSourcePrefix() )
			# use the folder name, as that is the convention with QMake,
			# e.g. prefix is subproject/src => baseName == src
			baseName = self.getProjectFileBaseName() or os.path.basename( sourceSubDir )
			if not self.getInSourceBuild():
				sourceDirectory = sourceSubDir

		projectFileName = "{0}.pro".format( baseName )
		return os.path.join( sourceDirectory, projectFileName )

	def createConfigureActions( self ):
		configuration = self.getInstructions()
		projectFile = self.getProjectFilePath()

		arguments = [ projectFile ]
		for variable in self.getQMakeVariables():
			arguments.append( str( variable ) )
		arguments.append( '{0}={1}'.format( self.getInstllPrefixVariableName(), configuration.getTargetDir() ) )
		self._setCommandArguments( arguments )

		super( QMakeBuilder, self ).createConfigureActions()

	def createConfMakeInstallActions( self ):
		# Stupidly, QMake doesn't have a standard way of installing to a prefix so just disable this
		if self.installEnabled():
			super( QMakeBuilder, self ).createConfMakeInstallActions()
		else:
			mApp().debugN( self, 3, 'Installation is not implemented by the project, not generating any actions.' )
			pass
