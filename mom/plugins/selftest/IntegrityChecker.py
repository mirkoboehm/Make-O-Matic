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

from mom.core.Exceptions import MomError
from mom.core.Plugin import Plugin
from mom.core.Project import Project
from mom.core.helpers.GlobalMApp import mApp
from mom.core.environments.Environments import Environments
from mom.core.Configuration import Configuration

class IntegrityChecker( Plugin ):

	def preFlightCheck( self ):
		def r( text ):
			raise MomError( "Error, integrity check failed: {0}".format( text ) )

		for project in mApp().getChildren():
			if not isinstance( project, Project ):
				r( "The top-level MApplication object may have Project objects as children only" )

			for childOfProject in project.getChildren():
				if not isinstance( childOfProject, ( Environments, Configuration ) ):
					r( "Project may have Environments and Configurations instances as children only" )
