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

from core.plugins.DoxygenGenerator import DoxygenGenerator
from core.plugins.RSyncPublisher import RSyncPublisher
from core.plugins.Preprocessor import Preprocessor
from core.helpers.PathResolver import PathResolver
from core.plugins.python.PythonConfiguration import PythonConfiguration
from core.helpers.BoilerPlate import getBuildProject
from core.plugins.python.PyUnitTester import PyUnitTester
import os

build, project = getBuildProject( projectName = 'Make-O-Matic', projectVersionNumber = '0.5.0',
								projectVersionName = 'French Fries', scmUrl = 'git://github.com/KDAB/Make-O-Matic.git' )

# add a preprocessor that generates the Doxygen input file
prep = Preprocessor( project, inputFilename = PathResolver( project.getSourceDir, 'doxygen.cfg.in' ),
					 outputFilename = PathResolver( project.getTempDir, 'doxygen.cfg' ) )
project.addPlugin( prep )

# add a doxygen generator
dox = DoxygenGenerator()
dox.setOptional( True )
dox.setDoxygenFile( prep.getOutputFilename() )
project.addPlugin( dox )

# set up configurations:
# python3 = Configuration( 'Python 3', project )
python26 = PythonConfiguration( 'Python 2.6', executable = 'python2.6', parent = project )
python26.addPlugin( PyUnitTester( testprogram = PathResolver( project.getSourceDir, os.path.join( 'tests', 'testsuite.py' ) ) ) )

# add a RSync publisher (remember to set the default upload location in the configuration file!):
project.addPlugin( RSyncPublisher( localDir = PathResolver( project.getDocsDir ) ) )

# run:
build.build()
