# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike@mikemcquaid.com>
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
import os
import shutil
import time

def rmtree( path ):
	if os.path.exists( path ):
		cwd = os.getcwd()
		realpath = os.path.realpath( path )
		os.chdir( os.path.expanduser( '~' ) )
		#FIXME Try and delete path twice (if needed) to work around stupid Windows race condition
		shutil.rmtree( realpath, True )
		if os.path.exists( realpath ):
			time.sleep( 15 )
			shutil.rmtree( realpath, False )
		os.chdir( cwd )
