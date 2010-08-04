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
from core.helpers.RunCommand import RunCommand
from core.Exceptions import MomError
import re

class BuildScriptInterface( MObject ):
	'''BuildScriptInterface encapsulates ways to invoke a build script.'''

	def __init__( self, buildScript, name = None ):
		MObject.__init__( self, name )
		self.setBuildScript( buildScript )

	def setBuildScript( self, script ):
		self.__buildScript = script

	def getBuildScript( self ):
		return self.__buildScript

	def querySetting( self, project, setting ):
		cmd = '{0} {1} query {2}'.format( sys.executable, self.getBuildScript(), setting )
		runner = RunCommand( cmd, 1800 )
		runner.run()
		if runner.getReturnCode() != 0:
			stderr = runner.getStdErr().decode()
			raise MomError( 'Cannot query setting "{0}" for build script "{1}": {2}!'\
				.format( setting, self.getBuildScript(), stderr ) )
		output = runner.getStdOut()
		if not output:
			raise MomError( 'The build script "{0}" did not specify a project name! It said: {1}'
				.format( self.getBuildScript(), stderr ) )
		line = output.decode().strip()
		groups = re.search( '^(.+?): (.+)$', line )
		if not groups:
			raise MomError( 'Did not understand this output: "{0}"!'.format( line ) )
		variable = groups.groups()[1]
		return variable

	def queryRevisionsSince( self, project, revision ):
		'''Execute the build script, and return the lines it outputs for "query revisions-since"'''
		cmd = '{0} {1} print revisions-since {2}'.format( sys.executable, self.getBuildScript(), revision )
		runner = RunCommand( cmd, 1800 )
		runner.run()
		if runner.getReturnCode() != 0:
			msg = 'Cannot get revision list for build script "{0}", continuing with next project.'\
				.format( self.getBuildScript() )
			raise MomError( msg )
		output = runner.getStdOut()
		if not output:
			return None
		lines = output.decode().split( '\n' )
		return lines

	def queryCurrentRevision( self, project ):
		cmd = '{0} {1} print current-revision'.format( sys.executable, self.getBuildScript() )
		runner = RunCommand( cmd, 1800 )
		runner.run()
		if runner.getReturnCode() != 0:
			raise MomError( 'Cannot get initial revision for build script "{0}".'.format( self.getBuildScript() ) )
		revision = runner.getStdOut().decode().strip()
		return revision
