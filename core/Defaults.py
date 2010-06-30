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
from core.MObject import MObject

class Defaults( MObject ):
	"""Defaults stores all hard-coded default values of make-o-matic."""

	def __init__( self ):
		'''Constructor'''
		MObject.__init__( self )

	def getExecutomatLogfileName( self ):
		return 'execution.log'

	def getProjectBuildSteps( self ):
		"""Return all defined build steps on the project level."""
		return [
			'project-create-folders',
			'project-checkout',
			'project-build-configurations',
			'project-create-docs',
			'project-package',
			'project-upload-docs',
			'project-upload-packages',
			'project-cleanup-docs',
			'project-cleanup-packages',
			'project-cleanup' ]

	def getProjectDefaultBuildSteps( self ):
		"""Returns the build steps enabled by default, per mode."""
		defaultSteps = {
			'c' : [ 'project-create-folders', 'project-checkout', 'project-build-configurations',
					'project-cleanup-packages', 'project-cleanup-docs', 'project-cleanup' ]
		# FIXME add other build modes
		}
		# FIXME verify that the defaults are actually known steps :-)
		return defaultSteps

