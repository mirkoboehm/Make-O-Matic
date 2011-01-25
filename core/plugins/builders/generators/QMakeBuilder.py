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

class QMakeBuilder( MakefileGeneratorBuilder ):
	'''QMakeBuilder generates the actions to build a project with qmake.'''

	def __init__( self, name = None, projectFile = None ):
		MakefileGeneratorBuilder.__init__( self, name )
		self.enableInstallation( False )
		self._projectFile = projectFile
		self._setCommand( "qmake" )

	def enableInstallation( self, onoff ):
		self.__install = onoff

	def installEnabled( self ):
		return self.__install

	def createConfigureActions( self ):
		if not self.getInSourceBuild():
			project = self.getInstructions().getProject()
			sourceDirectory = project.getSourceDir()
			if not self._projectFile:
				# If we don't have a project file, guess from the name
				# FIXME: We should probably check this somehow but can't be done until after preFlightCheck
				self._projectFile = "{0}.pro".format( project.getName() )
			projectFilePath = os.path.join( sourceDirectory, self._projectFile )
			self._setCommandArguments( [ projectFilePath ] )
		MakefileGeneratorBuilder.createConfigureActions( self )

	def createConfMakeInstallActions( self ):
		# Stupidly, QMake doesn't have a standard way of installing to a prefix so just disable this
		if self.installEnabled():
			super( QMakeBuilder, self ).createConfMakeInstallActions()
		else:
			mApp().debugN( self, 3, 'Installation is not implemented by the project, not generating any actions.' )
			pass
