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

from buildcontrol.simple_ci.SimpleCiBase import SimpleCiBase
from core.Exceptions import ConfigurationError, MomException
from core.helpers.GlobalMApp import mApp
import os
import time

class Slave( SimpleCiBase ):

	def getToolName( self ):
		return 'simpleci_slave'

	def execute( self ):
		self.debug( self, 'running in slave mode' )
		# we are now in slave mode
		# find the build scripts
		buildScripts = self.getParameters().getBuildScripts() or []
		if self.getParameters().getControlDir():
			baseDir = str( self.getParameters().getControlDir() )
			mApp().message( self, 'using "{0}" as control directory.'.format( baseDir ) )
			controlDir = os.path.normpath( os.path.join( os.getcwd(), baseDir ) )
			if not os.path.isdir( controlDir ):
				raise ConfigurationError( 'The control directory "{0}" does not exist!'.format( controlDir ) )
			folderScripts = filter( lambda x: x.endswith( '.py' ), os.listdir( controlDir ) )
			folderScripts = map( lambda x: controlDir + os.sep + x, folderScripts )
			folderScripts = map( lambda x: os.path.normpath( x ), folderScripts )
			buildScripts += folderScripts
		if not buildScripts:
			mApp().message( self, 'FYI: no build scripts specified.' )
		buildScripts = map( lambda x: os.path.normpath( os.path.abspath( x ) ), buildScripts )
		buildScripts = self.checkBuildScripts( buildScripts )
		# do the stuff
		sleepPeriod = 5 * 60 # if there was nothing to do, wait a little before retrying, to not hog the remote side
		try:
			if self.getParameters().getPerformTestBuilds():
				sleepPeriod = 0
				self.message( self, 'will do a test build for the latest revision of every build script' )
				self.runBuildScriptTestBuild( buildScripts )
			else:
				count = self.performBuilds( buildScripts )
				if count:
					sleepPeriod = 5 # just to avoid spawn races in case there is some problem
		except MomException as e:
			self.registerReturnCode( e.getReturnCode() )
			self.message( self, 'error during slave run, exit code {0}: {1}'.format( 
				self.getReturnCode(), e ) )
			sleepPeriod = 15 * 60 # if there is a problem, the process interrupts for a little longer, to allow for it to be fixed
		finally:
			if self.getParameters().getDelay():
				sleepPeriod = self.getParameters().getDelay()
			if sleepPeriod:
				self.debug( self, 'sleeping for {0} seconds.'.format( sleepPeriod ) )
				self.debugN( self, 2, 'Z' )
				self.debugN( self, 2, 'z' )
				self.debugN( self, 2, '.' )
				time.sleep( sleepPeriod )
			self.debug( self, 'done, exiting.' )
