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
from buildcontrol.mom.Remotebuilder import RemoteBuilder
from core.Parameters import Parameters
from core.loggers.ConsoleLogger import ConsoleLogger
from core.Settings import Settings
import sys

class ProxyBuilder( MApplication ):
	'''ProxyBuilder takes a few arguments that describe a remote build script, 
	and then executes that build script using a RemoteBuilder.'''

	def __init__( self, location, branch = None, tag = None, path = 'admin', script = 'buildscript.py' ):
		MApplication.__init__( self, name = 'proxybuilder' )
		self.addLogger( ConsoleLogger() )
		self.setDoBranchBuilds( False )
		self.__params = Parameters()
		self.__params.parse()
		self.__params.apply( self.getSettings() )
		self.getSettings().set( Settings.ScriptLogLevel, self.__params.getDebugLevel() )
		self.__location = location
		self.__branch = branch
		self.__tag = tag
		self.__path = path
		self.__script = script

	def getToolName( self ):
		return 'proxybuilder'

	def getParameters( self ):
		return self.__params

	def setDoBranchBuilds( self, onOff ):
		self.__doBranchBuilds = onOff

	def doBranchBuilds( self ):
		return self.__doBranchBuilds

	def execute( self ):
		location = self.getParameters().getScmLocation() or self.__location
		branch = self.getParameters().getBranch() or self.__branch
		tag = self.getParameters().getTag() or self.__tag
		builder = RemoteBuilder( location = location, branch = branch, tag = tag, path = self.__path, script = self.__script )
		builder.setRevision( self.getParameters().getRevision() )
		options = sys.argv[1:]
		# if location, branch or tag parameters are not specified on the command line, add the settings from 
		# the invoking script to the arguments:
		if not self.getParameters().getScmLocation() and location:
			options = [ '-u', location] + options
		if not self.getParameters().getBranch() and branch:
			options = [ '--branch', branch ] + options
		if not self.getParameters().getTag() and tag:
			options = [ '--tag', tag] + options
		mode = self.getSettings().get( Settings.ScriptRunMode )
		if mode == Settings.RunMode_Print and self.doBranchBuilds():
			command = self.getParameters().getArgs()[2]
			options = self.getParameters().getArgs()[3:]
			builder.getRevisionsSinceForBranchBuilds( command, options, location, branch, tag )
		else:
			runner = builder.invokeBuild( options )
			rc = runner.getReturnCode()
			self.registerReturnCode( rc )
