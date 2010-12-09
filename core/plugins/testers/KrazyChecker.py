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

from core.actions.ShellCommandAction import ShellCommandAction
from core.plugins.testers.Analyzer import Analyzer
from core.Project import Project
import os.path

# TODO: Move to an own module?
class CallbackShellCommandAction( ShellCommandAction ):

	def __init__( self, command = None, timeout = None, combineOutput = True, callback = None ):
		ShellCommandAction.__init__( self, command, timeout, combineOutput = combineOutput )
		self.__callback = callback

	def run( self ):
		try:
			return ShellCommandAction.run( self )
		finally:
			if self.__callback:
				self.__callback( self )

class KrazyChecker( Analyzer ):

	# config constants
	DefaultConfiguration = "configuration"

	def __init__( self, name = None ):
		Analyzer.__init__( self, name )
		self._setCommand( "krazy2" )

	def runMethod( self, action ):
		stdout = action._getRunner().getStdOut()
		self._saveXmlReport( stdout )
		self._saveHtmlReport( stdout )

		# TODO: Save score

	def _saveXmlReport( self, stdout ):
		if not stdout:
			return

		# TODO: Fix directory
		file = os.path.join( self.getInstructions().getBaseDir(), "krazy2.xml" )
		f = open( file, 'w' )
		f.write( stdout )
		f.close()

	def _saveHtmlReport( self, stdout ):
		if not stdout:
			return

		# WIP: XML --- XSLT 2.0 (lxml does not support that) ---> HTML

	def preFlightCheck( self ):
		assert isinstance( self.getInstructions(), Project )

		# check settings
		self.getSetting( KrazyChecker.DefaultConfiguration, True )

	def setup( self ):
		self._setCommand( "krazy2all" )
		argv = ["--verbose", "--export", "xml"]
		argv += self.getSetting( KrazyChecker.DefaultConfiguration, True )
		self._setCommandArguments( argv )

		action = CallbackShellCommandAction( self.getCommandWithArguments(), combineOutput = False, callback = self.runMethod )
		action.setWorkingDirectory( self.getInstructions().getSourceDir() )
		step = self.getInstructions().getStep( 'conf-make-test' )
		step.addMainAction( action )
		return Analyzer.setup( self )
