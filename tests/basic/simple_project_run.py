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

from core.Project import makeProject
from core.modules.DoxygenGenerator import DoxygenGenerator
from core.modules.publishers.RSyncPublisher import RSyncPublisher
from core.modules.Preprocessor import Preprocessor
from core.helpers.PathResolver import PathResolver
from core.Build import Build
from core.loggers.ConsoleLogger import ConsoleLogger
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
from core.Exceptions import MomException
import sys
from core.Configuration import Configuration

build = Build( minimumMomVersion = "0.5.0" )
# FIXME this should go into a convenience function to set up a standard build
build.getParameters().parse()
mApp().getSettings().set( Settings.ScriptLogLevel, build.getParameters().getDebugLevel() )
logger = ConsoleLogger()
build.addLogger( logger )
try:
	build._initialize()
except MomException as e:
	print( 'Error during setup, return code {0}: {1}'.format( e.getReturnCode() , str( e ) ), file = sys.stderr )
	sys.exit( e.getReturnCode() )
# ^^^

# FIXME this should all be one line
scmUrl = build.getParameters().getScmLocation() or 'git:git@gitorious.org:make-o-matic/mom.git'
project = makeProject( projectName = "Simple Project Run Test",
	projectVersionNumber = '0.5.0', projectVersionName = 'French Fries',
	scmUrl = scmUrl )
# ^^^
build.setProject( project )

# add a preprocessor that generates the Doxygen input file
prep = Preprocessor( project, inputFilename = PathResolver( project.getFolderManager().getSourceDir, 'doxygen.cfg.in' ),
					 outputFilename = PathResolver( project.getFolderManager().getTempDir, 'doxygen.cfg' ) )
project.addPlugin( prep )
# add a preprocessor that generates the Doxygen footer
#footer = Preprocessor( inputFilename = PathResolver( project.getFolderManager().getSourceDir, 'doxygen-footer.html.in' ),
#					 outputFilename = PathResolver( project.getFolderManager().getTempDir, 'doxygen-footer.html' ) )
#project.addPlugin( footer )
# add a doxygen generator
dox = DoxygenGenerator()
dox.setDoxygenFile( prep.getOutputFilename() )
project.addPlugin( dox )

# set up configurations:
python3 = Configuration( 'build using Python 3' )
project.addConfiguration( python3 )
python2 = Configuration( 'build using Python 2.6' )
project.addConfiguration( python2 )

# add a RSync publisher (remember to set the default upload location in the configuration file!):
project.addPlugin( RSyncPublisher( localDir = PathResolver( project.getFolderManager().getDocsDir ) ) )

# run:
build.build()
