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
from core.Defaults import Defaults
import os, sys
from core.Exceptions import ConfigurationError
from core.helpers.GlobalMApp import mApp
from core.helpers.NodeName import getNodeName
from core.helpers.TypeCheckers import check_for_nonempty_string
import traceback

class Settings( Defaults ):
	"""Settings stores all configurable values for a build script run."""

	def __init__( self ):
		Defaults.__init__( self )

		self.__settings = self.getDefaultSettings()

		if sys.platform == 'darwin' or sys.platform == 'win32':
			self.__momFolder = "Make-O-Matic"
		else:
			self.__momFolder = "mom"

	def getGlobalFolder( self, toolName = None ):
		if sys.platform == 'darwin':
			globalFolder = os.path.join( "/Library/Application Support", self.__momFolder )
		elif sys.platform == 'win32':
			globalFolder = os.path.join( os.getenv( 'ALLUSERSPROFILE' ), self.__momFolder )
		else:
			globalFolder = os.path.join( "/etc", self.__momFolder )

		if toolName:
			globalFolder = os.path.join( globalFolder, toolName )
		return globalFolder

	def getUserFolder( self, toolName = None ):
		if sys.platform == 'darwin':
			userFolder = os.path.join( "~/Library/Application Support", self.__momFolder )
			userFolder = os.path.expanduser( userFolder )
		elif sys.platform == 'win32':
			userFolder = os.path.join( os.getenv( 'APPDATA' ), self.__momFolder )
		else:
			userFolder = os.path.expanduser( "~/." + self.__momFolder )

		if toolName:
			userFolder = os.path.join( userFolder, toolName )
		return userFolder

	def evalConfigurationFiles( self, toolName = None ):
		folders = [ self.getGlobalFolder( toolName ), self.getUserFolder( toolName ) ]
		hostConfigFile = '{0}.py'.format( getNodeName() )
		files = [ 'config.py', hostConfigFile ]

		additionalConfigFile = mApp().getParameters().getConfigFile()
		if additionalConfigFile:
			if os.path.exists( additionalConfigFile ):
				files.append( additionalConfigFile )
			else:
				mApp().debug( self, "Warning: Not loading invalid config file: {0}".format( additionalConfigFile ) )

		for folder in folders:
			for fileName in files:
				configFile = os.path.join( folder, fileName )
				if not os.path.isfile( configFile ):
					mApp().debugN( self, 3, 'Configuration file "{0}" does not exist, continuing.'.format( configFile ) )
					continue
				mApp().debugN( self, 2, 'Loading configuration file "{0}"'.format( configFile ) )
				try:
					currentGlobals = {
						'__file__' : configFile,
						'application' : mApp()
					}
					execfile( configFile, currentGlobals )
					mApp().debug( self, 'Configuration file "{0}" loaded successfully'.format( configFile ) )
				except SyntaxError as e:
					mApp().debug( self, traceback.format_exc() )
					raise ConfigurationError( 'The configuration file "{0}" contains a syntax error: "{1}"'.format( configFile, str( e ) ) )
				except Exception as e: # we need to catch all exceptions, since we are calling user code
					mApp().debug( self, traceback.format_exc() )
					raise ConfigurationError( 'The configuration file "{0}" contains an error: "{1}"'.format( configFile, str( e ) ) )
				except: # we need to catch all exceptions, since we are calling user code
					mApp().debug( self, traceback.format_exc() )
					raise ConfigurationError( 'The configuration file "{0}" contains an unknown error!'.format( configFile ) )

	def getBuildTypeDescription( self, buildType ):
		descriptions = self.get( Settings.ProjectBuildTypeDescriptions )
		if buildType in descriptions:
			return descriptions[buildType]
		else:
			return None

	def setBuildStepEnabled( self, stepName, buildType, yesNo ):
		'''Enable or disable the specified build step, for the specified build type, in the defaults.
		This method needs to be called before the Instructions object set up the build sequence (e.g., before
		Instructions.setup() is called.'''
		check_for_nonempty_string( stepName, 'The step name needs to be a non-empty string!' )
		buildStepDescriptions = self.get( Settings.ProjectBuildSequence )
		for buildStepDescription in buildStepDescriptions:
			if buildStepDescription[0] == stepName:
				modes = buildStepDescription[1]
				modes = filter( lambda c: c not in buildType, modes )
				if yesNo:
					modes += buildType
				buildStepDescription[1] = modes
				mApp().debugN( self, 2, 'build step {0} is now enabled for the following build types: {1}'.format( stepName, modes ) )
				return
		raise ConfigurationError( 'The specified build type "{0}" is undefined!'.format( buildType ) )

	def getBuildStepEnabled( self, stepName, buildType ):
		'''Return whether a build step is enabled for a specified build type in the settings.'''
		check_for_nonempty_string( stepName, 'The step name needs to be a non-empty string!' )
		buildStepDescriptions = self.get( Settings.ProjectBuildSequence )
		for buildStepDescription in buildStepDescriptions:
			if buildStepDescription[0] == stepName:
				modes = buildStepDescription[1]
				return buildType in modes
		raise ConfigurationError( 'The specified build type "{0}" is undefined!'.format( buildType ) )

	def get( self, name, required = True, defaultValue = None ):
		check_for_nonempty_string( name, 'The setting name must be a nonempty string!' )
		try:
			return self.getSettings()[ name ]
		except KeyError:
			if required:
				raise ConfigurationError( 'The required setting "{0}" is undefined!'.format( name ) )
			else:
				return defaultValue

	def set( self, name, value ):
		check_for_nonempty_string( name, 'The setting name must be a nonempty string!' )
		self.getSettings()[ name ] = value

	def getSettings( self ):
		return self.__settings
