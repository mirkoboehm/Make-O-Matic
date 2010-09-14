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

from core.Settings import Settings
import os
from core.helpers.GlobalMApp import mApp

def extendDebugPrefix( token ):
	indentVar = mApp().getSettings().get( Settings.MomDebugIndentVariable )
	oldIndent = None
	if indentVar in os.environ:
		oldIndent = os.environ[ indentVar ]
	os.environ[ indentVar ] = '{0}{1}slave> '.format( oldIndent or '', ' ' if oldIndent else '' )
	return oldIndent

def restoreDebugPrefix( content ):
	indentVar = mApp().getSettings().get( Settings.MomDebugIndentVariable )
	os.environ[ indentVar ] = content or ''

def getDebugPrefix():
	indentVar = mApp().getSettings().get( Settings.MomDebugIndentVariable )
	if indentVar in os.environ:
		return os.environ[ indentVar ]
	else:
		return ''

