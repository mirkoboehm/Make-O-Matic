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

from core.modules.tools.doxygen.DoxygenGenerator import DoxygenGenerator
from core.modules.publishers.RSyncPublisher import RSyncPublisher
from core.modules.Preprocessor import Preprocessor
from core.helpers.PathResolver import PathResolver
from core.Configuration import Configuration
from core.helpers.BoilerPlate import setupStandardBuildAndProject

build, project = setupStandardBuildAndProject( projectName = 'MakeOMatic', minimumMomVersion = "0.5.0",
	projectVersionNumber = '0.5.0', projectVersionName = 'French Fries',
	scmUrl = 'git:git://gitorious.org/make-o-matic/mom.git' )

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
python3 = Configuration( 'test with Python 3', project )
python2 = Configuration( 'test with Python 2.6', project )

# add a RSync publisher (remember to set the default upload location in the configuration file!):
project.addPlugin( RSyncPublisher( localDir = PathResolver( project.getDocsDir ) ) )

# run:
build.build()
