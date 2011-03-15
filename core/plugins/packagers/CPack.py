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

from core.plugins.packagers.PackageProvider import PackageProvider
from core.actions.filesystem.FilesMoveAction import FilesMoveAction
from core.Exceptions import BuildError
from core.plugins.builders.generators.CMakeBuilder import getCMakeSearchPaths
import os
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
import re
from datetime import datetime
from core.actions.Action import Action

_CPackConfig = '''SET(CPACK_PACKAGE_NAME "@CPACK_PACKAGE_NAME@")
SET(CPACK_PACKAGE_NAME_SIMPLIFIED "@CPACK_PACKAGE_NAME_SIMPLIFIED@")
SET(CPACK_PACKAGE_VERSION_MAJOR "@CPACK_PACKAGE_VERSION_MAJOR@")
SET(CPACK_PACKAGE_VERSION_MINOR "@CPACK_PACKAGE_VERSION_MINOR@")
SET(CPACK_PACKAGE_VERSION_PATCH "@CPACK_PACKAGE_VERSION_PATCH@")
SET(CPACK_INSTALL_DIRECTORY "@CPACK_INSTALL_DIRECTORY@")
SET(CPACK_PACKAGE_SOURCE @CPACK_PACKAGE_SOURCE@)

SET(CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}")
GET_FILENAME_COMPONENT(CPACK_INSTALLED_DIRECTORIES "${CPACK_INSTALL_DIRECTORY}" REALPATH)
LIST(APPEND CPACK_INSTALLED_DIRECTORIES ".")

SET(CPACK_PACKAGE_NAME_AND_VERSION "${CPACK_PACKAGE_NAME} ${CPACK_PACKAGE_VERSION}")
IF(CPACK_PACKAGE_SOURCE)
	SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME_SIMPLIFIED}-${CPACK_PACKAGE_VERSION}-source")
	SET(CPACK_PACKAGE_NAME_AND_VERSION "${CPACK_PACKAGE_NAME_AND_VERSION} Source Code")
ENDIF()

IF(WIN32)
	IF(NOT CPACK_PACKAGE_SOURCE)
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME_AND_VERSION}")
	ENDIF()
	SET(CPACK_GENERATOR "@CPACK_GENERATOR_WINDOWS@")
	SET(CPACK_NSIS_DISPLAY_NAME "${CPACK_PACKAGE_NAME_AND_VERSION}")
	SET(CPACK_NSIS_PACKAGE_NAME "${CPACK_PACKAGE_NAME_AND_VERSION}")
	SET(CPACK_PACKAGE_INSTALL_REGISTRY_KEY "${CPACK_PACKAGE_NAME_AND_VERSION}")
ELSEIF(APPLE)
	IF(NOT CPACK_PACKAGE_SOURCE)
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}")
	ENDIF()
	SET(CPACK_GENERATOR "@CPACK_GENERATOR_APPLE@")
	SET(CPACK_SYSTEM_NAME "OSX")
ELSE()
	IF(NOT CPACK_PACKAGE_SOURCE)
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME_SIMPLIFIED}-${CPACK_PACKAGE_VERSION}")
	ENDIF()
	SET(CPACK_GENERATOR "@CPACK_GENERATOR_ELSE@")
ENDIF()

SET(CPACK_TOPLEVEL_TAG "${CPACK_SYSTEM_NAME}")
SET(CPACK_PACKAGE_INSTALL_DIRECTORY "${CPACK_PACKAGE_FILE_NAME}")
SET(CPACK_RESOURCE_FILE_LICENSE "@CPACK_RESOURCE_FILE_LICENSE@")
SET(CPACK_IGNORE_FILES "/\\\\.svn/;/\\\\.git/")
SET(CPACK_PACKAGE_DESCRIPTION "")
@CPACK_OPTIONAL_EXTRA_LOGIC@
'''

def fixCMakeWindowsPaths( path ):
	return path.replace( '\\', '\\\\' )

class _CPackMovePackageAction( FilesMoveAction ):
	def __init__( self, cpackAction, destination ):
		FilesMoveAction.__init__( self )
		self.__action = cpackAction
		self.setDestination( destination )

	def run( self ):
		"""Finds the names of the CPack generated packages and moves them."""
		if ( self.__action.getResult() != 0 ):
			self._setStdErr( ( 'CPack failed: %s' % self.__action.getStdErr() ).encode() )
			return 1
		lines = self.__action.getStdOut().splitlines()
		# This might break with newer versions. Tested with CPack 2.8.2 and 2.8.3
		packageRegex = re.compile( 'CPack: -? ?[Pp]ackage:? (.*) generated\.' )
		packageFiles = []
		for line in lines:
			line = line.decode()
			match = packageRegex.match( line )
			if match:
				packageFiles.append( match.group( 1 ) )
		self.setFiles( packageFiles )
		return FilesMoveAction.run( self )


class _CPackGenerateConfigurationAction( Action ):
	def __init__( self, sourcePackage, licenseFile, config, directory, sourceGenerators, binaryGenerators, extraCPackLogic ):
		Action.__init__( self )
		self._sourcePackage = sourcePackage
		self._licenseFile = licenseFile
		self._directory = directory
		self._config = config
		self._sourceGenerators = sourceGenerators
		self._binaryGenerators = binaryGenerators
		self._extraCPackLogic = extraCPackLogic

	def getLogDescription( self ):
		"""Provide a textual description for the Action that can be added to the execution log file."""
		return self.getName()

	def _formattedConfiguration( self ):
		config = _CPackConfig
		# Can't do this with str.format because of CMake's variable escaping conflicting
		# with Python's format escaping

		packageName = mApp().getSettings().get( Settings.ProjectName )
		packageNameSimplified = packageName.lower().replace( ' ', '_' )
		config = config.replace( "@CPACK_PACKAGE_NAME@", packageName, 1 )
		config = config.replace( "@CPACK_PACKAGE_NAME_SIMPLIFIED@", packageNameSimplified, 1 )

		versionList = mApp().getSettings().get( Settings.ProjectVersionNumber ).split( '.', 2 )
		config = config.replace( "@CPACK_PACKAGE_VERSION_MAJOR@", versionList[0] or 1, 1 )
		config = config.replace( "@CPACK_PACKAGE_VERSION_MINOR@", versionList[1] or 0, 1 )
		config = config.replace( "@CPACK_PACKAGE_VERSION_PATCH@", versionList[2] or 0, 1 )
		installDirectory = fixCMakeWindowsPaths( self._directory )
		config = config.replace( "@CPACK_INSTALL_DIRECTORY@", installDirectory, 1 )

		if self._extraCPackLogic:
			config = config.replace( "@CPACK_OPTIONAL_EXTRA_LOGIC@\n", self._extraCPackLogic )
		else:
			config = config.replace( "@CPACK_OPTIONAL_EXTRA_LOGIC@\n", '' )

		licenseFile = self._licenseFile

		if not licenseFile:
			licenseFile = os.path.join( self.getWorkingDirectory(), "CPackGeneratedLicense.txt" )
			with open( licenseFile, 'w' ) as license:
				license.write( '{0} - Copyright {1}, All Rights Reserved.'.format( packageName, datetime.now().year ) )
		else:
			licenseFile = os.path.abspath( licenseFile ) # NSIS apparently requires an absolute path to find the license file
		licenseFile = fixCMakeWindowsPaths( licenseFile )

		config = config.replace( "@CPACK_RESOURCE_FILE_LICENSE@", licenseFile )

		for platform in ( 'WINDOWS', 'APPLE', 'ELSE' ):
			if self._sourcePackage:
				generator = self._sourceGenerators[ platform ]
			else:
				generator = self._binaryGenerators[ platform ]
			config = config.replace( "@CPACK_GENERATOR_%s@" % platform, generator )

		if self._sourcePackage:
			cpackSource = "TRUE"
		else:
			cpackSource = "FALSE"
		config = config.replace( "@CPACK_PACKAGE_SOURCE@", cpackSource, 1 )
		return config

	def run( self ):
		"""Generates a CPack configuration file if needed."""
		config = os.path.join( self.getWorkingDirectory(), self._config )
		if ( os.path.exists( config ) ):
			return 0

		with open( config, 'w' ) as configFile:
			configFile.write( self._formattedConfiguration() )

		return 0


class CPack( PackageProvider ):

	def __init__( self, sourcePackage = False, licenseFile = None, extraCPackLogic = None, name = None ):
		PackageProvider.__init__( self, name )
		self._setCommand( "cpack" )
		self._setCommandSearchPaths( getCMakeSearchPaths() )

		if sourcePackage:
			self.__configFile = "CPackSourceConfig.cmake"
		else:
			self.__configFile = "CPackConfig.cmake"
		self._sourcePackage = sourcePackage
		self._setCommandArguments( [ "--verbose", "--config", self.__configFile ] )
		self._licenseFile = licenseFile
		self._extraCPackLogic = extraCPackLogic

	def _setLicenseFile( self, licenseFile ):
		self._licenseFile = licenseFile

	def makePackageStep( self ):
		"""Create packages for the project using CPack."""
		configuration = self.getInstructions()
		step = configuration.getStep( 'create-packages' )
		project = configuration.getProject()
		if self._sourcePackage:
			packagedDirectory = os.path.join( project.getSourceDir(), configuration.getSourcePrefix() )
		else:
			packagedDirectory = configuration.getTargetDir()
		generateConfig = _CPackGenerateConfigurationAction( self._sourcePackage, self._licenseFile, self.__configFile,
		                                                    packagedDirectory, self.sourceGenerators(), self.binaryGenerators(),
		                                                    self._extraCPackLogic )
		generateConfig.setWorkingDirectory( configuration.getBuildDir() )
		step.addMainAction( generateConfig )
		makePackage = PackageProvider.makePackageStep( self )
		movePackageDestination = self.getInstructions().getPackagesDir()
		movePackage = _CPackMovePackageAction( makePackage, movePackageDestination )
		step.addMainAction( movePackage )

	def sourceGenerators( self ):
		return { 'WINDOWS':'ZIP',
		         'APPLE':  'TBZ2',
		         'ELSE':   'TBZ2' }

	def binaryGenerators( self ):
		return { 'WINDOWS':'NSIS;ZIP',
		         'APPLE':  'DragNDrop;TBZ2',
		         'ELSE':   'STGZ;TBZ2' }
