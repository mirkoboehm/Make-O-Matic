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

from core.helpers.BoilerPlate import setupStandardBuildAndProject
from core.Configuration import Configuration
from core.helpers.PathResolver import PathResolver
from core.modules.publishers.RSyncPublisher import RSyncPublisher
from core.modules.tools.cmake.CMakeBuilder import CMakeBuilder, CMakeVariable
from core.modules.packagers.CPack import CPack
from core.modules.testers.CTest import CTest

build, project = setupStandardBuildAndProject( buildName = 'Charm', minimumMomVersion = "0.5.0",
	projectVersionNumber = '1.4.0',
	scmUrl = 'git:git://gitorious.org/charm/charm.git' )

# helper variable to set a CMake parameter
enableCharmTools = CMakeVariable( 'CHARM_ENABLE_TOOLS_BUILD', 'TRUE', 'BOOL' )

# find different Shared Debug build environments
# environments = Environments( [ 'Qt-4.[67].?-Shared-*' ], 'Qt 4', project )

# add a debug and a release configuration that build using CMake
debug = Configuration( 'Debug', project, )
cmakeDebug = CMakeBuilder()
cmakeDebug.setMakeOptions( '-j2' )
cmakeDebug.setMakeInstallOptions( '-j1' )
cmakeDebug.addCMakeVariable( enableCharmTools )
debug.addPlugin( cmakeDebug )

release = Configuration( 'Release', project )
cmakeRelease = CMakeBuilder()
cmakeRelease.setMakeOptions( '-j2' )
cmakeDebug.setMakeInstallOptions( '-j1' )
cmakeRelease.addCMakeVariable( enableCharmTools )
release.addPlugin( cmakeRelease )
release.addPlugin( CTest() )
release.addPlugin( CPack() )

# add a RSync publisher (remember to set the default upload location in the configuration file!):
project.addPlugin( RSyncPublisher( localDir = PathResolver( project.getPackagesDir ) ) )

build.build()
