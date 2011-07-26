# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Kevin Funk <kevin.funk@kdab.com>
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

import platform
import sys
from NodeName import getNodeName

def platform_details():
	if sys.platform == 'win32':
		return " ".join( platform.win32_ver() )
	elif sys.platform == 'darwin':
		return "{0} {1}".format( platform.mac_ver()[0], platform.mac_ver()[2] )
	elif 'linux' in sys.platform:
		return " ".join( platform.linux_distribution() )
	else:
		return "Unknown OS"

def machine_info():
	"""Returns a dict of machine information, like architecture or platform type"""

	info = {}
	info["sys-architecture"] = " ".join( platform.architecture() ).replace( "ELF", "" ).rstrip()
	info["sys-platform"] = platform.system().replace( "Darwin", "Mac OS X" )
	info["sys-nodename"] = getNodeName()
	info["sys-version"] = platform.version()
	info["sys-platform-details"] = platform_details()
	info["python-version"] = platform.python_version()
	return info
