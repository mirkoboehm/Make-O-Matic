# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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

from core.plugins.packagers.PackageProvider import PackageProvider
from core.plugins.builders import maketools

class MakePackager( PackageProvider ):

	def __init__( self, name = None ):
		PackageProvider.__init__( self, name )
		self.__makeTool = maketools.getMakeTool()
		self._setCommand( self.__makeTool.getCommand() )
		self._setCommandSearchPaths( self.__makeTool.getCommandSearchPaths() )
		self._setCommandArguments( ["package"] )

	def preFlightCheck( self ):
		self.__makeTool.checkVersion()
