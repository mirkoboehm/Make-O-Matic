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

class MomException( Exception ):
	"""MomException is the base class of all make-o-matic exceptions."""

	def __init__( self, value ):
		Exception.__init__( self )
		self.value = value

	def __str__( self ):
		return repr( self.value ).rstrip()

class BuildError( MomException ):
	"""A build error is raised if the build fails due to a problem caused by the project."""
	pass

class ConfigurationError( MomException ):
	"""A configuration error is raised if the build fails due to a mis-configuration of the run environment.
	The error is not caused by the project, and it is not an internal error in the make-o-matic code. 
	ConfigurationErrors need to be fixed by the administrators of the CI system."""

class MomError( MomException ):
	"""A MomError is raised if an error was detected that was caused by make-o-matic itself.
	MomErrors need to be fixed by the make-o-matic developers."""
	pass
