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
from core.actions.filesystem.FileMoveAction import FileMoveAction

class _CPackMovePackageAction( FileMoveAction ):
    def __init__( self, cpackAction, destination ):
        """Constructor"""
        FileMoveAction.__init__( self )
        self.__action = cpackAction
        self.setDestination( destination )

    def run( self ):
        """Executes the shell command. Needs a command to be set."""
        if (self.__action.getResult() != 0):
            return 1
        lines = self.__action.getStdOut().decode().split( '\n' )
        packageLine = lines[-2].rstrip()
        packageLine = packageLine.replace( 'CPack: Package ', '' )
        packageFileName = packageLine.replace( ' generated.', '' )
        self.setSource( packageFileName )
        return FileMoveAction.run( self )

class CPack( PackageProvider ):

    def __init__( self, name = None ):
        """Constructor"""
        PackageProvider.__init__( self, name )
        
    def _checkInstallation( self ):
        """Check if the package generator's prerequisite are installed."""
        runner = RunCommand( 'cpack --version' )
        runner.run()
        if runner.getReturnCode() != 0:
            raise ConfigurationError( "CPack::checkInstallation: cpack not found." )
        else:
            self._setDescription( runner.getStdOut().decode().rstrip() )
            mApp().debugN( self, 4, 'cpack found: "{0}"'.format( self.getDescription() ) )
        
    def makePackageStep( self ):
        """Create package for the project."""
        step = self.getInstructions().getExecutomat().getStep( 'conf-package' )
        buildDirectory = self.getInstructions().getFolderManager().getBuildDir()

        makePackage = ShellCommandAction( 'cpack' )
        makePackage.setWorkingDirectory( buildDirectory )
        step.addMainAction( makePackage )

        movePackageDestination = self.getInstructions().getProject().getFolderManager().getPackagesDir()
        movePackage = _CPackMovePackageAction( makePackage, movePackageDestination )
        step.addMainAction( movePackage )
