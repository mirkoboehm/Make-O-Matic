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
from core.MObject import MObject

class Instructions( MObject ):
	'''Instructions is the base class for anything that can be built by make-o-matic. 
	Projects are Instructions to build a Project.
	Configurations are Instructions to build a configuration of a Project.
	Instructions implement the phased approach to executing the build script, and the 
	idea of plug-ins that implement certain functionality.'''

	def __init__( self, name = None ):
		MObject.__init__( self, name )
		from core.executomat.Executomat import Executomat
		self.__executomat = Executomat( 'Exec-o-Matic' )
		self.__plugins = []
		self.__instructions = []

	def getExecutomat( self ):
		return self.__executomat

	def getPlugins( self ):
		return self.__plugins

	def addPlugin( self, plugin ):
		self.__plugins.append( plugin )

	def getChildren( self ):
		return self.__instructions

	def addChild( self, instructions ):
		assert isinstance( instructions, Instructions )
		self.__instructions.append( instructions )

	def runPreFlightChecks( self ):
		[ plugin.preFlightCheck( self ) for plugin in self.getPlugins() ]
		for child in self.getChildren():
			child.runPreFlightChecks()

	def runSetups( self ):
		[ plugin.setup( self ) for plugin in self.getPlugins() ]
		for child in self.getChildren():
			child.runSetups()

	def runWrapups( self ):
		[ plugin.wrapUp( self ) for plugin in self.getPlugins() ]
		for child in self.getChildren():
			child.runWrapups()

	def runShutDowns( self ):
		for plugin in self.getPlugins():
			try:
				plugin.shutDown( self )
			except Exception as e:
				text = '''\
An error occurred during shutdown: "{0}"
Offending module: "{1}" 
This error will not change the return code of the script!'''.format( str( e ), plugin.getName() )
				self.message( self, text )
		for child in self.getChildren():
			child.runShutDowns()
