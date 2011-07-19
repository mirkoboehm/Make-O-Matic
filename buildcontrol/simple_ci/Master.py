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

from buildcontrol.SubprocessHelpers import extend_debug_prefix, restore_debug_prefix
from buildcontrol.simple_ci.SimpleCiBase import SimpleCiBase
import os
import sys
import time

class Master( SimpleCiBase ):

	def getToolName( self ):
		return 'simpleci_master'

	def _buildAndReturn( self ):
		print( """\
+-+-+-+-+-+-+-+-+-+-+-+-+                     +-+ +-+-+-+-+ +-+-+-+-+
|m|a|k|e|-|o|-|m|a|t|i|c|                     |C| |K|D|A|B| |2|0|1|0|
+-+-+-+-+-+-+-+-+-+-+-+-+                     +-+ +-+-+-+-+ +-+-+-+-+
+-+ +-+-+-+-+-+ +-+ +-+-+-+-+-+ +-+-+-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
|i| |m|4|k|e|s| |u| |n|o|o|b|s| |k|n|o|w| |w|4|z|z| |f|0|0|b|4|r|3|d|
+-+ +-+-+-+-+-+ +-+ +-+-+-+-+-+ +-+-+-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
""" )
		while True:
			self.debug( self, 'running in master mode' )
			SimpleCiBase._buildAndReturn( self )
			if self.getParameters().getPerformTestBuilds():
				break
			period = 5
			self.debug( self, 'short break of {0} seconds'.format( period ) )
			time.sleep( period )

	def execute( self ):
		"""This is the main driver method when the control process is run as the master.
		In an endless loop, it invokes itself in slave mode to perform all builds that have accumulated since the last start.
		After every run, the master takes a short sleep."""
		# execute the build control process slave:
		cmd = '{0} {1}'.format( sys.executable, ' '.join( sys.argv + [ '--slave' ] ) )
		self.debug( self, '*** now starting slave CI process: {0} ***'.format( cmd ) )
		oldIndent = extend_debug_prefix( 'slave' )
		result = -1
		try:
			result = os.system( cmd ) # do not use RunCommand, it catches the output
		finally:
			restore_debug_prefix( oldIndent )
		self.debug( self, '*** slave finished with exit code {0}. ***'.format( result ) )
