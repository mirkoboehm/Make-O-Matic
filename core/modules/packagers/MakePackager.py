# This file is part of make-o-matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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

from core.modules.packagers.PackageProvider import PackageProvider
from core.executomat.ShellCommandAction import ShellCommandAction

class MakePackager( PackageProvider ):

	def __init__( self, name = None ):
		# FIXME Port to use Maketools
		"""Constructor"""
		PackageProvider.__init__( self, name )
		self._setCommand( "make" )

	def makePackageStep( self ):
		"""Create package for the project."""
		step = self.getInstructions().getStep( 'conf-package' )
		makePackage = ShellCommandAction( self.getCommand(), 'package' )
		makePackage.setWorkingDirectory( self.getInstructions().getBuildDir() )
		step.addMainAction( makePackage )
