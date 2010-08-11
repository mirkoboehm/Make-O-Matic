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

from core.Plugin import Plugin
from core.helpers.GlobalMApp import mApp
from core.helpers.TypeCheckers import check_for_nonempty_string
from core.Exceptions import AbstractMethodCalledError

class TestProvider( Plugin ):

    def __init__( self, name = None ):
        """Constructor"""
        Plugin.__init__( self, name )

    def _checkInstallation( self ):
        """Check if the tester's prerequisite are installed."""
        raise AbstractMethodCalledError

    def getDescription( self ):
        return self.__description

    def _setDescription( self, description ):
        check_for_nonempty_string( description, "The Tester description needs to be a non-empty string." )
        self.__description = description

    def makeTestStep( self ):
        """Run tests for the project."""
        raise AbstractMethodCalledError()

    def preFlightCheck( self ):
        """Overload"""
        self._checkInstallation()
        mApp().debug( self, 'Testing module initialized: {0}'.format( self.getDescription() ) )

    def setup( self ):
        """Setup is called after the test steps have been generated, and the command line 
        options have been applied to them. It can be used to insert actions into the build
        steps, for example."""
        self.makeTestStep()
