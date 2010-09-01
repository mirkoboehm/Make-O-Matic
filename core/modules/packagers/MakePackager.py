# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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

from core.modules.packagers.PackageProvider import PackageProvider
from core.executomat.ShellCommandAction import ShellCommandAction
from core.helpers.RunCommand import RunCommand
from core.Exceptions import ConfigurationError
from core.helpers.GlobalMApp import mApp

class MakePackager( PackageProvider ):

    def __init__( self, name = None ):
        """Constructor"""
        PackageProvider.__init__( self, name )

    def _checkInstallation( self ):
        """Check if the package generator's prerequisite are installed."""
        runner = RunCommand( 'make --version' )
        runner.run()
        if runner.getReturnCode() != 0:
            raise ConfigurationError( "MakePackager::checkInstallation: make not found." )
        else:
            lines = runner.getStdOut().decode().splitlines()
            self._setDescription( lines[0].rstrip() )
            mApp().debugN( self, 4, 'make found: "{0}"'.format( self.getDescription() ) )

    def makePackageStep( self ):
        """Create package for the project."""
        step = self.getInstructions().getStep( 'conf-package' )
        makePackage = ShellCommandAction( 'make package' )
        makePackage.setWorkingDirectory( self.getInstructions().getBuildDir() )
        step.addMainAction( makePackage )
