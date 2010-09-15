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
from core.Instructions import Instructions
from core.executomat.Executomat import Executomat
import os
from core.helpers.GlobalMApp import mApp
from core.Exceptions import MomError, ConfigurationError
from core.Defaults import Defaults
from core.helpers.TimeKeeper import formattedTime

class BuildInstructions( Instructions ):
	def __init__( self, name = None, parent = None ):
		Instructions.__init__( self, name, parent )
		self.__executomat = Executomat( 'Exec-o-Matic' )

	def _getExecutomat( self ):
		return self.__executomat

	def getStep( self, step ):
		return self._getExecutomat().getStep( step )

	def describe( self, prefix ):
		Instructions.describe( self, prefix )
		self._getExecutomat().describe( prefix + '    ' )

	def createXmlNode( self, document ):
		node = Instructions.createXmlNode( self, document )
		node.attributes["starttime"] = str ( formattedTime( self._getExecutomat().getTimeKeeper().getStartTime() ) )
		node.attributes["stoptime"] = str ( formattedTime( self._getExecutomat().getTimeKeeper().getStopTime() ) )
		node.attributes["timing"] = str( self._getExecutomat().getTimeKeeper().deltaString() )

		stepsElement = document.createElement( "steps" )
		for step in self._getExecutomat()._getSteps():
			element = step.createXmlNode( document )
			stepsElement.appendChild( element )
		node.appendChild( stepsElement )

		return node

	def _configureBaseDir( self ):
		assert self.getParent()
		parentBaseDir = self.getParent().getBaseDir()
		assert os.path.isdir( parentBaseDir )
		baseDirName = self._getBaseDirName()
		baseDir = os.path.join( parentBaseDir, baseDirName )
		if os.path.isdir( baseDir ):
			raise MomError( 'Base directory for a build instructions object exists!' )
		try:
			os.makedirs( baseDir )
			self._setBaseDir( baseDir )
		except ( OSError, IOError ) as e:
			raise ConfigurationError( 'Cannot create required base directory "{0}" for {1}: {2}!'
				.format( baseDir, self.getName(), e ) )

	def _getLogDir( self ):
		return self._getExecutomat().getLogDir()

	def _configureLogDir( self ):
		assert self.getParent()
		logDirName = self._getBaseDirName()
		parentLogDir = self.getParent()._getLogDir()
		assert os.path.isdir( parentLogDir )
		logDir = os.path.abspath( os.path.join( parentLogDir, logDirName ) )
		try:
			os.makedirs( logDir )
			self._getExecutomat().setLogfileName( mApp().getSettings().get( Defaults.ProjectExecutomatLogfileName ) )
			self._getExecutomat().setLogDir( logDir )
		except ( OSError, IOError )as e:
			raise ConfigurationError( 'Cannot create required log directory "{0}" for {1}: {2}!'
				.format( logDir, self.getName(), e ) )

	def runSetups( self ):
		self._configureBaseDir()
		self._configureLogDir()
		Instructions.runSetups( self )

