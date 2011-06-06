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
from buildcontrol.simple_ci.SelfUpdater import SelfUpdater
from core.helpers.RunCommand import RunCommand
from core.helpers.GlobalMApp import mApp

class GitRepoSelfUpdater( SelfUpdater ):
	def __init__( self, name = None ):
		SelfUpdater.__init__( self, name )
		self.setUseRebase( False )

	def getUseRebase( self ):
		return self.__useRebase

	def setUseRebase( self, onOff ):
		self.__useRebase = onOff

	def update( self, folder ):
		cmd = [ 'git', 'pull' ]
		if self.getUseRebase():
			cmd.append( '--rebase' )
		runner = RunCommand( cmd )
		runner.setWorkingDir( folder )
		runner.run()
		if runner.getReturnCode() == 0:
			mApp().debugN( self, 2, 'Updated the git repository at "{0}"'.format( folder ) )
		else:
			# we are not raising an exception, because we do not want the master to die because of, for example, a temporary 
			# network outage
			message = runner.getStdErrAsString()
			mApp().message( self, 'Updating the git repository at "{0}" failed: "{1}"'.format( folder, message ) )
