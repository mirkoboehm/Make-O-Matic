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

from core.Project import Project
from core.modules.scm.SCMGit import SCMGit
from core.modules.DoxygenGenerator import DoxygenGenerator
from core.modules.reporters.ConsoleReporter import ConsoleReporter
from core.modules.publishers.RSyncPublisher import RSyncPublisher
from core.modules.Preprocessor import Preprocessor
from core.helpers.PathResolver import PathResolver
from core.Settings import Settings

project = Project( "Simple Project Run Test", "0.5.0" )
project.getSettings().set( Settings.ProjectVersionNumber, '0.5.0' )
project.getSettings().set( Settings.ProjectVersionName, 'French Fries' )

# add a console reporter
reporter = ConsoleReporter()
project.addPlugin( reporter )

# add a git SCM
scm = SCMGit()
scm.setSrcDir( 'src' )
scm.setRevision( 'HEAD' )
scm.setUrl( 'git@gitorious.org:make-o-matic/mom.git' )
# scm.setUrl( 'file:////d/kdab/products/charm/src' )
project.setScm( scm )

# add a preprocessor that generates the Doxygen input file
prep = Preprocessor( inputFilename = PathResolver( project.getFolderManager().getSourceDir, 'doxygen.cfg.in' ),
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

# add a RSync publisher:
rsync = RSyncPublisher( uploadLocation = 'localhost://home/mirko/temp',
					localDir = PathResolver( project.getFolderManager().getDocsDir ) )
project.addPlugin( rsync )

# run:
project.build()
