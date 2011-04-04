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

from core.Plugin import Plugin
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings

class Reporter( Plugin ):

	def __init__( self, name = None ):
		Plugin.__init__( self, name )

	def sendReport( self ):
		"""Implement this for creating and sending your report

		\note This is run during the shutdown phase"""

		raise NotImplementedError()

	def shutDown( self ):
		reportingEnabled = mApp().getSettings().get( Settings.ScriptEnableReporting )
		if not reportingEnabled:
			mApp().debug( self, "Not sending report, disabled by settings (Settings.ScriptEnableReporting)" )
			return

		self.sendReport()
