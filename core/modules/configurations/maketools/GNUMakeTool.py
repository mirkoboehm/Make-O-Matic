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
from core.Exceptions import ConfigurationError
from core.helpers.GlobalMApp import mApp
from core.helpers.RunCommand import RunCommand
from core.modules.configurations.maketools.MakeTool import MakeTool

class GNUMakeTool( MakeTool ):
	'''GNUMakeTool implements a class for a the GNU Make makefile tool.'''

	def __init__( self ):
		MakeTool.__init__( self )
		self.setCommand( 'make' )

	def getVersion( self ):
		runner = RunCommand( [ self.getCommand(), "--version" ] )
		runner.run()
		if runner.getReturnCode() != 0:
			raise ConfigurationError( 'GNUMakeTool: GNU Make not found.' )
		description = runner.getStdOut().decode().split( '\n' )[0].rstrip()
		mApp().debugN( self, 4, 'GNU Make found: "{0}"'.format( description ) )
		return description

	def getArguments( self ):
		return [ '-j{0}'.format( self._getJobs() )  ]
