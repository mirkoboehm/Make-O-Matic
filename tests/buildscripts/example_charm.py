#!/usr/bin/env python

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

from core.helpers.BoilerPlate import BuildProject
from core.Configuration import Configuration
from core.helpers.PathResolver import PathResolver
from core.plugins.RSyncPublisher import RSyncPublisher
from core.plugins.builders.generators.CMakeBuilder import CMakeBuilder, CMakeVariable
from core.plugins.packagers.CPack import CPack
from core.plugins.testers.CTest import CTest
from core.environments.Environments import Environments

build, project = BuildProject( 'Charm', 'git://github.com/KDAB/Charm.git', '1.4.0', build = 'Charm Build' )

# helper variable to set a CMake parameter
enableCharmTools = CMakeVariable( 'CHARM_ENABLE_TOOLS_BUILD', 'TRUE', 'BOOL' )

sharedDebug = Environments( [ 'Qt-4.[67].?-Shared-Debug' ], 'Qt 4 Shared Debug', project )
debug = Configuration( 'Debug', sharedDebug, )
cmakeDebug = CMakeBuilder()
cmakeDebug.addCMakeVariable( enableCharmTools )
debug.addPlugin( cmakeDebug )

sharedRelease = Environments( [ 'Qt-4.[67].?-Shared-Release' ], 'Qt 4 Shared Release', project )
release = Configuration( 'Release', sharedRelease )
cmakeRelease = CMakeBuilder()
cmakeRelease.addCMakeVariable( enableCharmTools )
release.addPlugin( cmakeRelease )
release.addPlugin( CTest() )
release.addPlugin( CPack( licenseFile = 'License.txt' ) )

# add a RSync publisher (remember to set the default upload location in the configuration file!):
project.addPlugin( RSyncPublisher( localDir = PathResolver( project.getPackagesDir ) ) )

build.build()
