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
import unittest
from cases.buildstatus_persistence_tests import BuildStatusPersistenceTests
from cases.path_resolver_tests import PathResolverTest
from cases.preprocessor_tests import PreprocessorTest
from cases.run_mode_print_tests import RunModePrintTests
from cases.run_timeout_tests import RunWithTimeoutTest
from cases.scm_factory_tests import ScmFactoryTests
from cases.buildscript_interface_tests import BuildScriptInterfaceTests
from selftest.simple_project_tests import SimpleProjectTests
from selftest.simple_ci_tests import SimpleCITests
from selftest.charm_build_tests import CharmBuildTests

classes = [ BuildStatusPersistenceTests,
	PathResolverTest,
	PreprocessorTest,
	RunModePrintTests,
	RunWithTimeoutTest,
	ScmFactoryTests,
	SimpleProjectTests,
	BuildScriptInterfaceTests,
	CharmBuildTests,
	SimpleCITests
]

s = unittest.TestSuite( map( unittest.TestLoader().loadTestsFromTestCase, classes ) )
unittest.TextTestRunner( verbosity = 2 ).run( s )
