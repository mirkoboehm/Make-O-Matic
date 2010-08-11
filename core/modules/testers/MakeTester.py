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

from core.modules.testers.TestProvider import TestProvider
from core.executomat.ShellCommandAction import ShellCommandAction
from core.helpers.RunCommand import RunCommand
from core.Exceptions import ConfigurationError
from core.helpers.GlobalMApp import mApp

class MakeTester( TestProvider ):

    def __init__( self, name = None ):
        """Constructor"""
        TestProvider.__init__( self, name )
        
    def _checkInstallation( self ):
        """Check if the tester's prerequisite are installed."""
        runner = RunCommand( 'make --version' )
        runner.run()
        if runner.getReturnCode() != 0:
            raise ConfigurationError( "MakeTester::checkInstallation: make not found." )
        else:
            lines = runner.getStdOut().decode().split( '\n' )
            self._setDescription( lines[0].rstrip() )
            mApp().debugN( self, 4, 'make found: "{0}"'.format( self.getDescription() ) )
        
    def makeTestStep( self ):
        """Run tests for the project."""
        step = self.getInstructions().getExecutomat().getStep( 'conf-make-test' )
        makeTest = ShellCommandAction( 'make test' )
        makeTest.setWorkingDirectory( self.getInstructions().getFolderManager().getBuildDir() )
        step.addMainAction( makeTest )
        