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
from core.plugins.builders.generators.CMakeBuilder import CMakeSearchPaths
import os
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings

_CPackConfig = '''SET(CPACK_PACKAGE_NAME "@CPACK_PACKAGE_NAME@")
SET(CPACK_PACKAGE_VERSION_MAJOR "@CPACK_PACKAGE_VERSION_MAJOR@")
SET(CPACK_PACKAGE_VERSION_MINOR "@CPACK_PACKAGE_VERSION_MINOR@")
SET(CPACK_PACKAGE_VERSION_PATCH "@CPACK_PACKAGE_VERSION_PATCH@")
SET(CPACK_INSTALL_DIRECTORY "@CPACK_INSTALL_DIRECTORY@")
SET(CPACK_PACKAGE_SOURCE @CPACK_PACKAGE_SOURCE@)

SET(CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}")
GET_FILENAME_COMPONENT(CPACK_INSTALLED_DIRECTORIES "${CPACK_INSTALL_DIRECTORY}" REALPATH)
LIST(APPEND CPACK_INSTALLED_DIRECTORIES ".")

IF(WIN32)
	IF(CPACK_PACKAGE_SOURCE)
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME} ${CPACK_PACKAGE_VERSION} Source")
	ELSE()
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME} ${CPACK_PACKAGE_VERSION}")
	ENDIF()
	SET(CPACK_GENERATOR "@CPACK_GENERATOR_WINDOWS@")
	SET(CPACK_NSIS_DISPLAY_NAME "${CPACK_PACKAGE_FILE_NAME}")
	SET(CPACK_NSIS_PACKAGE_NAME "${CPACK_PACKAGE_FILE_NAME}")
	SET(CPACK_PACKAGE_INSTALL_REGISTRY_KEY "${CPACK_PACKAGE_FILE_NAME}")
ELSEIF(APPLE)
	IF(CPACK_PACKAGE_SOURCE)
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-Source")
	ELSE()
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}")
	ENDIF()
	SET(CPACK_GENERATOR "@CPACK_GENERATOR_APPLE@")
	SET(CPACK_SYSTEM_NAME "OSX")
ELSE()
	IF(CPACK_PACKAGE_SOURCE)
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-Source")
	ELSE()
		SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}")
	ENDIF()
	SET(CPACK_GENERATOR "@CPACK_GENERATOR_ELSE@")
ENDIF()

SET(CPACK_TOPLEVEL_TAG "${CPACK_SYSTEM_NAME}")
SET(CPACK_PACKAGE_INSTALL_DIRECTORY "${CPACK_PACKAGE_FILE_NAME}")
SET(CPACK_RESOURCE_FILE_LICENSE "@CPACK_RESOURCE_FILE_LICENSE@")
SET(CPACK_IGNORE_FILES "/\\\\.svn/;/\\\\.git/")
SET(CPACK_PACKAGE_DESCRIPTION "")
'''

class _CPackMovePackageAction( FilesMoveAction ):
	def __init__( self, cpackAction, destination ):
		FilesMoveAction.__init__( self )
		self.__action = cpackAction
		self.setDestination( destination )

	def run( self ):
		"""Finds the names of the CPack generated packages and moves them."""
		if ( self.__action.getResult() != 0 ):
			return 1
		lines = self.__action.getStdOut().splitlines()
		packageLinePrefix = 'CPack: Package '
		packageLineSuffix = ' generated.'
		packageFiles = []
		for line in lines:
			line = line.decode()
			if line.startswith( packageLinePrefix ) and line.endswith( packageLineSuffix ):
				line = line.replace( packageLinePrefix, '' )
				packageFile = line.replace( packageLineSuffix, '' )
				packageFiles.append( packageFile )
		self.setFiles( packageFiles )
		return FilesMoveAction.run( self )


class _CPackGenerateConfigurationAction( FilesMoveAction ):
	def __init__( self, sourcePackage, config, directory ):
		FilesMoveAction.__init__( self )
		self._sourcePackage = sourcePackage
		self._directory = directory
		self._config = config

	def _formattedConfiguration( self ):
		config = _CPackConfig
		# Can't do this with str.format because of CMake's variable escaping conflicting
		# with Python's format escaping
		config = config.replace( "@CPACK_PACKAGE_NAME@", mApp().getSettings().get( Settings.ProjectName ), 1 )

		versionList = mApp().getSettings().get( Settings.ProjectVersionNumber ).split( '.', 2 )
		config = config.replace( "@CPACK_PACKAGE_VERSION_MAJOR@", versionList[0] or 1, 1 )
		config = config.replace( "@CPACK_PACKAGE_VERSION_MINOR@", versionList[1] or 0, 1 )
		config = config.replace( "@CPACK_PACKAGE_VERSION_PATCH@", versionList[2] or 0, 1 )
		config = config.replace( "@CPACK_INSTALL_DIRECTORY@", self._directory, 1 )

		licenseFile = self._licenseFile if self._licenseFile != None else ""

		config = config.replace( "@CPACK_RESOURCE_FILE_LICENSE@", licenseFile )

		generators = { ('WINDOWS',True): 'ZIP',
					   ('WINDOWS',False): 'NSIS;ZIP',
					   ('APPLE', True): 'TBZ2',
					   ('APPLE', False): 'DragNDrop;TBZ2',
					   ('ELSE', True): 'TBZ2',
					   ('ELSE', False): 'STGZ;TBZ2' }

		for i in ('WINDOWS', 'APPLE', 'ELSE'):
			config = config.replace( "@CPACK_GENERATOR_%s@" % i, generators[(i, self._sourcePackage)] )

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

	def __init__( self, sourcePackage = False, licenseFile = None, name = None ):
		PackageProvider.__init__( self, name )
		self._licenseFile = licenseFile
		self._setCommand( "cpack", CMakeSearchPaths )

		if licenseFile == None and not sourcePackage:
			raise ConfigurationError( 'CPack requires a license file for binary packages!' )
		elif len( licenseFile ) > 0 and sourcePackage:
			raise ConfigurationError( 'You must not set a license file for source packages!' )

		if sourcePackage:
			self.__configFile = "CPackSourceConfig.cmake"
		else:
			self.__configFile = "CPackConfig.cmake"
		self._sourcePackage = sourcePackage
		self._setPackageArguments( [ "--verbose", "--config", self.__configFile ] )

	def makePackageStep( self ):
		"""Create packages for the project using CPack."""
		configuration = self.getInstructions()
		step = configuration.getStep( 'conf-package' )
		project = configuration.getProject()
		if self._sourcePackage:
			packagedDirectory = os.path.join( project.getSourceDir(), configuration.getSourcePrefix() )
		else:
			packagedDirectory = configuration.getTargetDir()
		generateConfig = _CPackGenerateConfigurationAction( self._sourcePackage, self.__configFile, packagedDirectory )
		generateConfig.setWorkingDirectory( configuration.getBuildDir() )
		step.addMainAction( generateConfig )
		makePackage = PackageProvider.makePackageStep( self )
		movePackageDestination = project.getPackagesDir()
		movePackage = _CPackMovePackageAction( makePackage, movePackageDestination )
		step.addMainAction( movePackage )
