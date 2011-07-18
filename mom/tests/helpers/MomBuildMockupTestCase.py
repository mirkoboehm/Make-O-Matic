# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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

from core.Project import Project
from core.Settings import Settings
from core.environments.Environments import Environments
from core.Configuration import Configuration
from core.Build import Build
from mom.tests.helpers.MomTestCase import MomTestCase
import os
import sys
from core.helpers.SafeDeleteTree import rmtree
from core.plugins.DoxygenGenerator import DoxygenGenerator

class MomBuildMockupTestCase( MomTestCase ):
	'''MomTestCase is a base test case class that sets up and tears down the Build object.'''

	def setUp( self, useScm = False, useEnvironments = False ):
		MomTestCase.setUp( self, False )

		sys.argv = [] # reset command line arguments

		build = Build( name = 'XmlReportTestBuild' )
		project = Project( 'XmlReportTestProject' )
		build.setProject( project )

		if useScm:
			project.createScm( 'git://github.com/KDAB/Make-O-Matic.git' )

		if useEnvironments:
			environments = Environments( [ 'dep-a-1.?.0' ], 'Test dependency', project )
		else:
			environments = Environments()

		# add some plugin
		dox = DoxygenGenerator()
		dox.setEnabled( False )
		project.addPlugin( dox )

		# add some configurations
		Configuration( 'Debug', environments )
		Configuration( 'Release', environments )

		build.getSettings().set( Settings.EnvironmentsBaseDir, self.TEST_MOM_ENVIRONMENTS )

		self.build = build
		self.project = project
		self.cwd = os.getcwd()

	def tearDown( self ):
		MomTestCase.tearDown( self )
		os.chdir( self.cwd )
		rmtree( "xmlreporttestbuild" )
