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

# import from root mom namespace, not $CWD/mom, use absolute_import for this (since v2.5).
from __future__ import absolute_import
from mom.core.Settings import Settings
from mom.core.helpers.GlobalMApp import mApp
import os

def extend_debug_prefix( token ):
	indentVar = mApp().getSettings().get( Settings.MomDebugIndentVariable )
	oldIndent = None
	if indentVar in os.environ:
		oldIndent = os.environ[ indentVar ]
	elements = filter( lambda x: x, [ oldIndent, token ] )
	os.environ[ indentVar ] = ' '.join( elements )
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
