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
from core.helpers.GlobalMApp import mApp
from core.executomat.Executomat import Executomat
from core.Settings import Settings
from core.helpers.FilesystemAccess import make_foldername_from_string
import os
from core.Exceptions import ConfigurationError, MomError, MomException
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none, check_for_nonempty_string
from core.Defaults import Defaults

class Instructions( MObject ):
	'''Instructions is the base class for anything that can be built by make-o-matic. 
	Projects are Instructions to build a Project.
	Configurations are Instructions to build a configuration of a Project.
	Instructions implement the phased approach to executing the build script, and the 
	idea of plug-ins that implement certain functionality.'''

	def __init__( self, name = None, parent = None ):
		MObject.__init__( self, name )
		self.__executomat = Executomat( 'Exec-o-Matic' )
		self._setBaseDir( None )
		self._setParent( None )
		if parent: # the parent instructions object
			parent.addChild( self )
		self.__plugins = []
		self.__instructions = []

	def _setParent( self, parent ):
		assert parent == None or isinstance( parent, Instructions )
		self.__parent = parent

	def getParent( self ):
		return self.__parent

	def _setBaseDir( self, folder ):
		check_for_nonempty_string_or_none( folder, 'The instructions base directory must be a folder name, or None!' )
		self.__baseDir = folder

	def getBaseDir( self ):
		try:
			check_for_nonempty_string( self.__baseDir, 'basedir can only be queried after preFlightCheck!' )
		except MomException:
			mApp().debugN( self, 4, 'getBaseDir() was called before the base directory was set!' )
			raise
		return self.__baseDir

	def getExecutomat( self ):
		return self.__executomat

	def getPlugins( self ):
		return self.__plugins

	def addPlugin( self, plugin ):
		plugin._setInstructions( self )
		self.__plugins.append( plugin )

	def getChildren( self ):
		return self.__instructions

	def addChild( self, instructions ):
		assert isinstance( instructions, Instructions )
		if instructions in self.getChildren():
			raise MomError( 'A child can be added to the same instruction object only once (offending object: {0})!'
				.format( instructions.getName() ) )
		instructions._setParent( self )
		self.__instructions.append( instructions )

	def removeChild( self, instructions ):
		assert isinstance( instructions, Instructions )
		if instructions in self.getChildren():
			self.getChildren().remove( instructions )
		else:
			raise MomError( 'Cannot remove child {0}, I am not it\'s parent {1}!'
				.format( instructions.getName(), self.getName() ) )

	def execute( self ):
		'''If execute is implemented, it is supposed to execute the pay load of the instructions. 
		Execute is not required, many modules only need to act during the different phases.
		To implement specific operations between setup and wrap-up, re-implement execute.'''
		pass

	def describe( self, prefix ):
		MObject.describe( self, prefix )
		basedir = '(not set)'
		try:
			basedir = self.getBaseDir()
		except ConfigurationError:
			pass
		me = '{0}- base dir: {1}'.format( prefix, basedir )
		print( me )
		subPrefix = prefix + '    '
		for plugin in self.getPlugins():
			plugin.describe( subPrefix )
		self.getExecutomat().describe( subPrefix )

	def describeRecursively( self, prefix = '' ):
		'''Describe this instruction object in human readable form.'''
		self.describe( prefix )
		prefix = '    {0}'.format( prefix )
		for child in self.getChildren():
			child.describeRecursively( prefix )

	def _getIndex( self, instructions ):
		index = 0
		for child in self.getChildren():
			if child == instructions:
				return index
			index = index + 1
		raise MomError( 'Unknown child {0}'.format( instructions ) )

	def _getBaseDirName( self ):
		myIndex = None
		if self.getParent():
			myIndex = self.getParent()._getIndex( self ) + 1
		if self.getName() == self.__class__.__name__:
			baseDirName = '{0}'.format( myIndex )
		else:
			index = myIndex or ''
			spacer = '_' if myIndex else ''
			baseDirName = '{0}{1}{2}'.format( index, spacer, make_foldername_from_string( self.getName() ) )
		return baseDirName

	def _configureBaseDir( self ):
		parentBaseDir = os.getcwd()
		if self.getParent():
			parentBaseDir = self.getParent().getBaseDir()
		assert os.path.isdir( parentBaseDir )
		baseDirName = self._getBaseDirName()
		baseDir = os.path.join( parentBaseDir, baseDirName )
		try:
			os.makedirs( baseDir )
			self._setBaseDir( baseDir )
		except ( OSError, IOError ) as e:
			raise ConfigurationError( 'Cannot create required base directory "{0}" for {1}: {2}!'
				.format( baseDir, self.getName(), e ) )
		if not self.getParent():
			os.chdir( baseDir )

	def _configureLogDir( self ):
		# FIXME it is not "ProjectLogDir" anymore
		logDirName = self._getBaseDirName()
		parentLogDir = self.getBaseDir()
			# bootstrap if this is the root object
		if self.getParent():
			parentLogDir = self.getParent().getExecutomat().getLogDir()
		else:
			parentLogDir = self.getBaseDir()
			logDirName = self.getSettings().get( Defaults.ProjectLogDir )
		assert os.path.isdir( parentLogDir )
		logDir = os.path.abspath( os.path.join( parentLogDir, logDirName ) )
		try:
			os.makedirs( logDir )
			self.getExecutomat().setLogDir( logDir )
		except ( OSError, IOError )as e:
			raise ConfigurationError( 'Cannot create required log directory "{0}" for {1}: {2}!'
				.format( logDir, self.getName(), e ) )


	def runPreFlightChecks( self ):
		mApp().debugN( self, 2, 'performing pre-flight checks' )
		[ plugin.preFlightCheck() for plugin in self.getPlugins() ]
		[ child.runPreFlightChecks() for child in self.getChildren() ]

	def runSetups( self ):
		mApp().debugN( self, 2, 'setting up' )
		self._configureBaseDir()
		self._configureLogDir()
		self.__executomat.setLogfileName( mApp().getSettings().get( Settings.ProjectExecutomatLogfileName ) )
		[ plugin.setup() for plugin in self.getPlugins() ]
		for child in self.getChildren():
			child.runSetups()

	def runWrapups( self ):
		mApp().debugN( self, 2, 'wrapping up' )
		[ plugin.wrapUp() for plugin in self.getPlugins() ]
		for child in self.getChildren():
			child.runWrapups()

	def runShutDowns( self ):
		for child in self.getChildren():
			child.runShutDowns()
		mApp().debugN( self, 2, 'shutting down' )
		for plugin in self.getPlugins():
			try:
				plugin.shutDown()
			except Exception as e:
				text = '''\
An error occurred during shutdown: "{0}"
Offending module: "{1}" 
This error will not change the return code of the script!'''.format( str( e ), plugin.getName() )
				mApp().message( self, text )

