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
from core.loggers.ConsoleLogger import ConsoleLogger
from core.modules.DoxygenGenerator import DoxygenGenerator
from core.modules.reporters.ConsoleReporter import ConsoleReporter

project = Project( "Simple Project Run Test", "0.5.0" )
# add a console logger
logger = ConsoleLogger()
logger.setLevel( 1 )
project.addLogger( logger )

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

# add a doxygen generator
dox = DoxygenGenerator()
dox.setDoxygenFile( 'doxygen.cfg' )
project.addPlugin( dox )

# run:
project.build()
