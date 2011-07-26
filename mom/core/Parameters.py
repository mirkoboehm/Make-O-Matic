# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko@kdab.com>
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

from mom.core.MObject import MObject
from mom.core.helpers.GlobalMApp import mApp
from mom.core.helpers.StringUtils import IndentedHelpFormatterWithNL
import optparse
import sys

class Parameters( MObject ):
	'''Parameters parses and stores the command line parameters (arguments) of a script.'''

	def __init__( self, name = None ):
		MObject.__init__( self, name )

		parser = self._createOptionParser()
		self.setParser( parser )
		( self.__options, self.__args ) = self.__parser.parse_args() # populate options and args

	def _getOptions( self ):
		return self.__options

	def getArgs( self ):
		return self.__args

	def getDescription( self ):
		return ""

	def setParser( self, parser ):
		self.__parser = parser

	def getParser( self ):
		return self.__parser

	def _createOptionParser( self ):
		usage = "usage: %prog [options] [build|describe|query <setting>|print]"
		version = 'Make-O-Matic {0}'.format( mApp().getMomVersion() )
		description = self.getDescription()
		epilog = '''\
https://github.com/KDAB/Make-O-Matic
http://docs.kdab.com/make-o-matic/{0}/html

'''.format( mApp().getMomVersion() )

		parser = optparse.OptionParser( usage = usage, version = version, description = description,
				epilog = epilog, formatter = IndentedHelpFormatterWithNL() )
		self._initParser( parser )
		return parser

	def _initParser( self, parser ):
		group = parser.add_option_group( "Default options" )
		group.add_option( '-l', '--load-config-file', action = 'store', dest = 'configFile',
			help = 'additional config file which will be loaded during startup' )
		group.add_option( '-v', '--verbosity', action = 'count', dest = 'verbosity', default = 0,
			help = 'set the level of debug output (-v, -vv, -vvv...)' )

	def parse( self ):
		""" read program execution options, setting up variables and proceed the dependent steps"""

		( self.__options, self.__args ) = self.__parser.parse_args( sys.argv )

	def getConfigFile( self ):
		return self._getOptions().configFile

	def getDebugLevel( self ):
		return self._getOptions().verbosity
