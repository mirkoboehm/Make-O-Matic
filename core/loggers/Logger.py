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
from datetime import datetime
import os
from core.MObject import MObject
from core.Exceptions import AbstractMethodCalledError

class Logger( MObject ):
	"""Logger is the base class for Logger objects."""

	def __init__( self, name ):
		"""Constructor"""
		MObject.__init__( self, name )

	def message( self, mobject, msg ):
		raise AbstractMethodCalledError()

	def debug( self, mobject, msg ):
		raise AbstractMethodCalledError()

	def debugN( self, mobject, level , msg ):
		raise AbstractMethodCalledError()

	def timeStampPrefix( self ):
		return datetime.now().strftime( '%y%m%d-%H:%M:%S' ) + ' '

	def messagePrefix( self ):
		prefix = ''
		try:
			prefix = os.environ['AUTOBUILD_DEBUG_INDENT']
		except: pass
		return prefix
