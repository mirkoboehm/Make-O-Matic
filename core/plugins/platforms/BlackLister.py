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

from core.plugins.platforms.Selector import Selector
from core.Exceptions import AbortBuildException
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp

class BlackLister( Selector ):
	"""BlackLister is used to prevent builds on specific blacklisted platforms.
	If the specified environment variable matches the pattern, the build is aborted during the prepare phase without an error."""

	def __init__( self, variable = None, pattern = None, name = None ):
		Selector.__init__( self, variable = variable, pattern = pattern, name = name )

	def prepare( self ):
		currentMode = mApp().getSettings().get( Settings.ScriptRunMode )
		if currentMode != Settings.RunMode_Build:
			mApp().debug( self , "Not in build mode, not checking platform" )
			return

		if self._isMatch():
			text = 'BlackLister aborted build because variable "{0}" matches regex "{1}"'\
				.format( self.getVariableName(), self.getValuePattern() )
			raise AbortBuildException( text )
		else:
			pass # all platforms with not matching variables are selected
