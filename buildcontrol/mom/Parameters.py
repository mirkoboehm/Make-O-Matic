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
from core.MObject import MObject
import sys
from core.Exceptions import ConfigurationError
from core.helpers.GlobalMApp import mApp
import optparse
import os
from core.Settings import Settings

class Parameters( MObject ):
	'''Parse the parameters of an invocation of the mom tool.'''

	def __init__( self, name = None ):
		MObject.__init__( self, name )

	def getRevision( self ):
		return self.__revision

	def getBuildScriptOptions( self ):
		return self.__buildScriptOptions

	def getUrl( self ):
		return self.__url

	def getPath( self ):
		return self.__path

	def parse( self ):
		'''The mom command line contains two parts, a set of options for the mom tool itself, and a set of options for the 
		invoked build script. The latter are ignored by mom, and will be passed down to the build script only. Both sections are 
		separated by a single dash. If the single dash is not found, it is assumed that all parameters are to be parsed by the mom 
		tool. Example: 
		mom -vv -u git:git://gitorious.org/make-o-matic/mom.git -p mom/buildscript.py -r4711 - -vv -t H -r4711
		'''
		# split up the command line into the two sections: 
		index = 0
		momOptions = sys.argv[:]
		self.__buildScriptOptions = []
		for item in sys.argv:
			if item.strip() == '-':
				momOptions = sys.argv[0:index]
				self.__buildScriptOptions = sys.argv[index + 1:]
				break
			index = index + 1
		mApp().debugN( self, 2, 'mom tool options: {0}'.format( ' '.join( momOptions ) ) )
		# set up the parser:
		parser = optparse.OptionParser()
		parser.add_option( '-r', '--revision', action = 'store', dest = 'revision',
			help = 'build script revision to be retrieved' )
		parser.add_option( '-u', '--scm-url', action = 'store', dest = 'url',
			help = 'SCM location including SCM identifier' )
		parser.add_option( '-p', '--path', action = 'store', dest = 'buildscriptPath',
			help = 'path of the build script in the specified repository' )
		parser.add_option( '-v', '--verbose', action = 'count', dest = 'verbosity', default = 0,
			help = 'level of debug output' )
		# parse options:
		( options, args ) = parser.parse_args( momOptions )
		if options.revision:
			self.__revision = options.revision
		else:
			raise ConfigurationError( 'No revision specified!' )
		if options.url:
			self.__url = options.url
		else:
			raise ConfigurationError( 'No SCM URL specified!' )
		if options.buildscriptPath:
			self.__path = options.buildscriptPath
		else:
			self.__path = os.path.join( 'mom', 'buildscript.py' )
			mApp().message( self, 'no build script path specified, using "{0}"'.format( self.__path ) )
		if options.verbosity:
			mApp().getSettings().set( Settings.ScriptLogLevel, options.verbosity )
		if len( args ) > 1: # the one element is the program path
			raise ConfigurationError( 'The mom tool does not understand any extra arguments (arguments found: {0})!'
				.format( ' '.join( args ) ) )
