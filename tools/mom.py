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
from core.MApplication import MApplication
from core.Settings import Settings
from core.loggers.ConsoleLogger import ConsoleLogger
from buildcontrol.mom.Parameters import Parameters
from core.helpers.GlobalMApp import mApp

class MomRemoteRunner( MApplication ):
	'''MomRemoteRunner takes the location descriptor of a remote build script, fetches the build script, 
	and executes it locally.'''

	def __init__( self ):
		MApplication.__init__( self, name = 'mom' )
		self.__parameters = Parameters()

	def getToolName( self ):
		return 'mom'

	def getParameters( self ):
		return self.__parameters

	def execute( self ):
		mApp().debugN( self, 2, 'build script options: {0}'.format( ' '.join( self.getParameters().getBuildScriptOptions() ) ) )
		# fetch the directory with the specified build script
		# ...
		# execute the build script:
		pass

	def build( self ):
		self.__parameters.parse()
		settings = self.getSettings()
		settings.set( Settings.ScriptLogLevel, 3 ) # FIXME
		self.addLogger( ConsoleLogger() )
		settings.evalConfigurationFiles( self.getToolName() )
		self.debug( self, 'debug level is {0}'.format( settings.get( Settings.ScriptLogLevel ) ) )
		MApplication.build( self )

if __name__ == "__main__":
	mom = MomRemoteRunner()
	mom.build()

