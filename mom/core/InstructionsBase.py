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

from mom.core.MObject import MObject

class InstructionsBase( MObject ):

	def prepare( self ):
		'''Execute the prepare phase for this object.'''
		pass

	def preFlightCheck( self ):
		'''Execute the pre-flight check phase for this object.'''
		pass

	def setup( self ):
		'''Execute the setup phase for this object.'''
		pass

	def execute( self ):
		'''Execute the execute phase for this object.
		If execute is implemented, it is supposed to execute the pay load of the instructions. 
		Execute is not required, many modules only need to act during the different phases.
		To implement specific operations between setup and wrap-up, re-implement execute.'''
		pass

	def wrapup( self ):
		'''Execute the wrapup phase for this object.'''
		pass

	def report( self ):
		"""Report is called after the build has finished. Plug-ins that generate reports 
		about the build should overload this method."""
		pass

	def notify( self ):
		"""Send out notifications about the build process. Plug-ins that, for example, send 
		emails, create chat notifications or talk to remote servers should overload this 
		method."""
		pass

	def shutDown( self ):
		'''Execute the shut down phase for this object.'''
		pass
