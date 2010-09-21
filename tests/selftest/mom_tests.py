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
from tests.helpers.MomTestCase import MomTestCase
from buildcontrol.mom.Parameters import Parameters
import sys
import unittest
from core.modules.scm.RevisionInfo import RevisionInfo
from buildcontrol.mom.Remotebuilder import RemoteBuilder

class MomTests( MomTestCase ):
	'''MomTests tests the mom remote runner tool.'''

	def testParseParameters( self ):
		'''Verify that the parser passes the correct subset of arguments to the remote build script.'''
		buildscriptArgs = [ '-vv', '-t', 'H', '-r', '4711' ]
		momArgs = [ sys.argv[0], '-vv', '-u', 'git:git://gitorious.org/make-o-matic/mom.git',
			'-p', 'mom/buildscript.py', '-r', '4711', '-' ]
		args = momArgs + buildscriptArgs
		params = Parameters()
		params.parse( args )
		self.assertEqual( buildscriptArgs, params.getBuildScriptOptions() )

	def testFetchRemoteBuildscript( self ):
		revInfo = RevisionInfo()
		revInfo.revision = 'HEAD'
		name = 'buildscript.py'
		path = 'admin'
		location = 'git:git://github.com/KDAB/Make-O-Matic.git'
		remote = RemoteBuilder( revInfo, location = location, path = path, script = name )
		try:
			remote.fetchBuildScript()
		except Exception as e:
			self.fail( 'fetching the remote build script fails: {0}'.format( e ) )

if __name__ == "__main__":
	unittest.main()
