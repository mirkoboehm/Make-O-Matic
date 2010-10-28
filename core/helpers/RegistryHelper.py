# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
#
# Make-O-Matic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Make-O-Matic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <http://www.gnu.org/licenses/>.
from core.helpers.TypeCheckers import check_for_nonempty_string
import os
from core.Exceptions import ConfigurationError
try:
	import winreg
except ImportError:
	import _winreg as winreg

def getPathFromRegistry( key ):
	check_for_nonempty_string( key, "The registry key needs to be a non-empty string" )

	hkeystring, _, key = key.partition( os.path.sep )
	key, _, value = key.rpartition( os.path.sep )

	if hkeystring is "HKEY_CURRENT_USER":
		hkey = winreg.HKEY_CURRENT_USER
	elif hkeystring is "HKEY_LOCAL_MACHINE":
		hkey = winreg.HKEY_LOCAL_MACHINE
	else:
		raise ConfigurationError( "getPathFromRegistry currently only supports HKEY_CURRENT_USER and HKEY_LOCAL_MACHINE." )
	with winreg.OpenKey( hkey, key ) as registrykey:
		registryvalue, _ = winreg.QueryValueEx( registrykey, value )
		return registryvalue
