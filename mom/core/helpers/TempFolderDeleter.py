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
from mom.core.helpers.TypeCheckers import check_for_list_of_paths
import shutil
from mom.core.helpers.GlobalMApp import mApp

class TempFolderDeleter( object ):

	def __init__( self, folders ):
		check_for_list_of_paths( folders, 'The list of temporary folders must contain paths or resolvers!' )
		self.__folders = folders

	def __enter__( self ):
		pass

	def __exit__( self, type, value, traceback ):
		for tempdir in self.__folders:
			try:
				shutil.rmtree( tempdir, ignore_errors = True )
			except:
				mApp().debug( self, 'Cannot delete temporary directory "{0}" (ignored).'.format( tempdir ) )
