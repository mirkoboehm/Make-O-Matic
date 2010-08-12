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

from core.helpers.TypeCheckers import check_for_nonempty_string, check_for_nonnegative_int
from core.Exceptions import MomError
from core.helpers.RunCommand import RunCommand
from core.executomat.Action import Action
from shutil import move

class FileMoveAction( Action ):
    """FileMoveAction encapsulates the execution of one command in the Step class. 
    It is mostly used internally, but can be of general use as well."""
    def __init__( self, source = None, destination = None ):
        Action.__init__( self )
        self.setSource( source )
        self.setDestination( destination )
        
    def setSource( self, source ):
        """Set the source file location to move"""
        self.__source = source
        
    def getSource( self ):
        """Get the source file location to move"""
        return self.__source
    
    def setDestination( self, destination ):
        """Set the destination file location to move to"""
        self.__destination = destination
        
    def getDestination( self ):
        """Get the destination file location to move to"""
        return self.__destination

    def getLogDescription( self ):
        """Provide a textual description for the Action that can be added to the execution log file."""
        return self.getName()

    def run( self ):
        """Executes the shell command. Needs a command to be set."""
        try:
            move( self.__source, self.__destination )
        except:
            return 1
        return 0
