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

from __future__ import unicode_literals

def check_python_version():
	# in this case, hard coded values make sense, because we do not even want to initialize the Settings object before 
	# verifying the Python version:
	import sys
	requiredMajor = 2
	requiredMinor = 6
	detectedMajor = sys.version_info[0]
	detectedMinor = sys.version_info[1]
	detectedMicro = sys.version_info[2]
	if detectedMajor >= requiredMajor:
		return
	else:
		if detectedMajor == requiredMajor and detectedMinor >= requiredMinor:
			return
	# use old syntax :-) :
	print( 'This Python interpreter is too old. Despite the beautiful plumage, it is almost deceased. ' +
			'Required version: ' + str( requiredMajor )
			+ '.' + str( requiredMinor )
			+ '. Detected version: ' + str( detectedMajor )
			+ '.' + str( detectedMinor )
			+ '.' + str( detectedMicro )
			+ '.' )
	sys.exit( 1 )

# this code will be executed during import:
check_python_version()

