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

from core.plugins.DoxygenGenerator import DoxygenGenerator
from core.plugins.Preprocessor import Preprocessor
from core.helpers.PathResolver import PathResolver
from core.configurations.PythonConfiguration import PythonConfiguration
from core.helpers.BoilerPlate import BuildProject
from core.plugins.python.PyUnitTester import PyUnitTester
from core.plugins.python.PyLintChecker import PyLintChecker
import os

build, project = BuildProject( name = 'Make-O-Matic', version = '0.5.0',
								versionName = 'French Fries', url = 'git://github.com/KDAB/Make-O-Matic.git' )

# add a preprocessor that generates the Doxygen input file
prep = Preprocessor( project, inputFilename = PathResolver( project.getSourceDir, 'doxygen.cfg.in' ),
					 outputFilename = PathResolver( project.getTempDir, 'doxygen.cfg' ) )
project.addPlugin( prep )
footer = Preprocessor( project, inputFilename = PathResolver( project.getSourceDir, 'doxygen-footer.html.in' ),
					 outputFilename = PathResolver( project.getTempDir, 'doxygen-footer.html' ) )
project.addPlugin( footer )

# add a doxygen generator
dox = DoxygenGenerator()
dox.setOptional( True )
dox.setDoxygenFile( prep.getOutputFilename() )
project.addPlugin( dox )

# set up configurations:
# python3 = Configuration( 'Python 3', project )
python2 = PythonConfiguration( 'Python 2', executable = 'python', parent = project )
python2.addPlugin( PyUnitTester( testprogram = PathResolver( project.getSourceDir, os.path.join( 'tests', 'testsuite_selftest.py' ) ) ) )

pylint = PyLintChecker( pyLintTool = 'pylint-2.6',
	pyLintRcFile = PathResolver( project.getSourceDir, 'pylintrc' ),
	htmlOutputPath = PathResolver( project.getDocsDir, 'pylint.html' ),
	modules = [ 'core', 'buildcontrol', 'tools', 'tests' ],
	minimumSuccessRate = 0.75
	)
pylint.setOptional( True )
python2.addPlugin( pylint )

# run:
build.build()
