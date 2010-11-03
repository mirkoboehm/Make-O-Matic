# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <krf@electrostorm.net>
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

from __future__ import with_statement
from tests.helpers.MomTestCase import MomTestCase
from core.helpers.GlobalMApp import mApp
import unittest
from core.Exceptions import ConfigurationError

class SettingsTests ( MomTestCase ):

	def testSetBuildStepEnabled( self ):
		step = 'project-upload-packages'
		self.assertFalse( mApp().getSettings().getBuildStepEnabled( step, 'c' ) )
		mApp().getSettings().setBuildStepEnabled( step, 'c', True )
		self.assertTrue( mApp().getSettings().getBuildStepEnabled( step, 'c' ) )
		mApp().getSettings().setBuildStepEnabled( step, 'c', False )
		self.assertFalse( mApp().getSettings().getBuildStepEnabled( step, 'c' ) )

	def testSetBuildStepEnabledInvalidStep( self ):
		step = 'project-xyz'
		def call():
			mApp().getSettings().setBuildStepEnabled( step, 'z', True )
		# Py3 can use a with statement for that, much nicer:
		self.assertRaises( ConfigurationError, call )


if __name__ == "__main__":
	unittest.main()
