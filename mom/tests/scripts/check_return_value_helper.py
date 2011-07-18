#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Make-O-Matic.
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
from __future__ import print_function
import sys

# This file simply returns the integer return code it gets as a parameter.
# It is used to test the RunCommand class.
if len( sys.argv ) != 2:
	print( 'Integer argument required!' )
	sys.exit( 1 )

try:
	returncode = int( sys.argv[1] )
	sys.exit( returncode )
except Exception as e:
	print( 'Integer argument required: {0}'.format( e ), file = sys.stderr )
	sys.exit( 1 )
