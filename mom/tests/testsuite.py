#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Make-O-Matic.
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

import sys
import unittest

print( sys.path )

from mom.core.Exceptions import MomException, ConfigurationError
from mom.core.MApplication import MApplication
from mom.plugins.DoxygenGenerator import DoxygenGenerator
from mom.plugins.builders.generators.CMakeBuilder import CMakeBuilder
from mom.plugins.builders.generators.QMakeBuilder import QMakeBuilder
from mom.plugins.builders.maketools import getMakeTool, getMakeToolNames
from mom.plugins.packagers.CPack import CPack
from mom.plugins.publishers.RSyncPublisher import RSyncPublisher
from mom.plugins.python.PyLintChecker import PyLintChecker
from mom.plugins.sourcecode.SCMGit import SCMGit
from mom.plugins.sourcecode.SCMSubversion import SCMSubversion
from mom.plugins.testers.CTest import CTest
from mom.tests.buildcontrol.BuildScriptInterfaceTests import BuildScriptInterfaceTests
from mom.tests.buildcontrol.BuildStatusPersistenceTests import BuildStatusPersistenceTests
from mom.tests.core.MApplicationTests import MApplicationTests
from mom.tests.core.RunModeDescribeTests import RunModeDescribeTests
from mom.tests.core.RunModePrintTests import RunModePrintTests
from mom.tests.core.SettingsTests import SettingsTests
from mom.tests.core.actions.FileSystemActionsTests import FileSystemActionsTests
from mom.tests.core.environments.EnvironmentTests import EnvironmentTests
from mom.tests.core.helpers.EnvironmentSaverTest import EnvironmentSaverTest
from mom.tests.core.helpers.PathResolverTests import PathResolverTests
from mom.tests.core.helpers.SettingResolverTests import SettingResolverTests
from mom.tests.core.helpers.TemplateSupportTests import TemplateSupportTests
from mom.tests.core.helpers.XmlReportTests import XmlReportTests
from mom.tests.plugins.AnalyzerTests import AnalyzerTests
from mom.tests.plugins.EmailReporterTest import EmailReporterTest
from mom.tests.plugins.PreprocessorTests import PreprocessorTests
from mom.tests.plugins.PyUnitTesterTests import PyUnitTesterTests
from mom.tests.plugins.QTestTests import QTestTests
from mom.tests.plugins.ScmFactoryTests import ScmFactoryTests
from mom.tests.plugins.ScmGitTests import ScmGitTests
from mom.tests.plugins.ScmSvnTests import ScmSvnTests
from mom.tests.selftest.charm_build_tests import CharmBuildTests
from mom.tests.selftest.environment_setup_tests import EnvironmentSetupTests
from mom.tests.selftest.run_timeout_tests import RunWithTimeoutTests
from mom.tests.selftest.simple_ci_tests import SimpleCITests
from mom.tests.selftest.simple_project_tests import SimpleProjectTests

#from mom.tests.cases.emailer_tests import EmailerTest

CLASSES = [
	# self tests first
	CharmBuildTests,
	EnvironmentSetupTests,
	SimpleProjectTests,
	SimpleCITests,

	# others
	AnalyzerTests,
	EnvironmentTests,
	BuildScriptInterfaceTests,
	BuildStatusPersistenceTests,
#	EmailerTest,
	EmailReporterTest,
	EnvironmentSaverTest,
	FileSystemActionsTests,
	PathResolverTests,
	PreprocessorTests,
	PyUnitTesterTests,
	RunModePrintTests,
	RunModeDescribeTests,
	RunWithTimeoutTests,
	ScmFactoryTests,
	ScmGitTests,
	ScmSvnTests,
	XmlReportTests,
	SettingsTests,
	TemplateSupportTests,
	QTestTests,
	SettingResolverTests,
	MApplicationTests
]

DEPENDENCIES = [
	SCMGit,
	SCMSubversion,
	RSyncPublisher,
]

OPTIONAL_DEPENDENCIES = [
	DoxygenGenerator,
]

CXX_DEPENDENCIES = [
	CMakeBuilder,
	QMakeBuilder,
	CTest,
	CPack
]

PYTHON_DEPENDENCIES = [
	PyLintChecker,
]

def check_dependencies():

	def check_plugins( plugins ):
		failed_list = []
		for plugin_class in plugins:
			plugin = plugin_class()
			try:
				plugin.resolveCommand()
			except ( MomException, ConfigurationError ):
				# try to get a sane plugin identifier
				if hasattr( plugin, 'getCommand' ):
					pluginName = plugin.getCommand()
				if not pluginName and hasattr( plugin, 'getName' ):
					pluginName = plugin.getName()
				if not pluginName:
					pluginName = plugin.__class__.__name__
				assert( pluginName )

				failed_list.append( pluginName )
		return failed_list

	def print_warning( missing_list, optional = False, type = '' ):
		if not missing_list:
			return

		type = type + ' '
		missing = ' '.join( missing_list )
		if optional:
			force = 'may'
		else:
			force = 'will'
		print( "WARNING: You appear to be missing some {0}dependencies: {1}".format( type, missing ) )
		print( "This {0} cause test failures and will break some {1}functionality.".format( force, type ) )

	MApplication()

	missing = check_plugins( DEPENDENCIES )
	try:
		import lxml
		lxml.__path__ # remove unused warning
	except ImportError:
		missing.append( 'lxml' )

	optional_missing = check_plugins( OPTIONAL_DEPENDENCIES )

	cxx_missing = check_plugins( CXX_DEPENDENCIES )
	try:
		getMakeTool().checkVersion()
	except ( MomException, ConfigurationError ):
		cxx_missing.append( '/'.join( getMakeToolNames() ) )
	python_missing = check_plugins( PYTHON_DEPENDENCIES )

	print_warning( missing )
	print_warning( optional_missing, True, 'optional' )
	print_warning( cxx_missing, True, 'C++' )
	print_warning( python_missing, True, 'Python' )

	# check if this was called directly, if yes: wait for user input on missing deps
	if __name__ == "__main__":
		if missing or optional_missing or cxx_missing or python_missing:
			try:
				raw_input( 'Press "Enter" to continue...' )
			except KeyboardInterrupt:
				print( '' )
				sys.exit( 1 )

def main():
	check_dependencies()

	suite = unittest.TestSuite( map( unittest.TestLoader().loadTestsFromTestCase, CLASSES ) )
	result = unittest.TextTestRunner( verbosity = 2 ).run( suite )

	sys.stderr.flush()
	sys.stdout.flush()

	if result.wasSuccessful():
		print( 'Tests completed successfully.' )
		sys.exit( 0 )
	else:
		print( 'Tests failed.' )
		sys.exit( 1 )

if __name__ == "__main__":
	main()
