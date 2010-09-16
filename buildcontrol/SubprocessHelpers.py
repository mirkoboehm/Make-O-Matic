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

from core.Settings import Settings
import os
from core.helpers.GlobalMApp import mApp

def extend_debug_prefix( token ):
	indentVar = mApp().getSettings().get( Settings.MomDebugIndentVariable )
	oldIndent = None
	if indentVar in os.environ:
		oldIndent = os.environ[ indentVar ]
	os.environ[ indentVar ] = '{0}{1}slave> '.format( oldIndent or '', ' ' if oldIndent else '' )
	return oldIndent

def restore_debug_prefix( content ):
	indentVar = mApp().getSettings().get( Settings.MomDebugIndentVariable )
	os.environ[ indentVar ] = content or ''

def get_debug_prefix():
	indentVar = mApp().getSettings().get( Settings.MomDebugIndentVariable )
	if indentVar in os.environ:
		return os.environ[ indentVar ]
	else:
		return ''

