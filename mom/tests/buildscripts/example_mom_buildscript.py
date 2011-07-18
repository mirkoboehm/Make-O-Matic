#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Make-O-Matic.
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

from core.configurations.PythonConfiguration import PythonConfiguration
from core.helpers.BoilerPlate import BuildProject

build, project = BuildProject( 'Make-O-Matic', 'git://github.com/KDAB/Make-O-Matic.git', '0.5.0', versionName = 'French Fries' )

# set up configurations:
python = PythonConfiguration( 'Python', parent = project )
# Hint: do not enable running the test suite here, because this script is part of the test suite :-)
# python.addPlugin( PyUnitTester( testprogram = PathResolver( project.getSourceDir, os.path.join( 'tests', 'testsuite.py' ) ) ) )

# run:
build.build()
