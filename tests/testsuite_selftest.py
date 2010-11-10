#!/usr/bin/env python

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

import os
import sys

def main():
	filePath = os.path.realpath( os.path.dirname( __file__ ) )
	momDirectory = os.path.abspath( os.path.join( filePath, '..' ) )

	sys.path.insert( 0, momDirectory )
	print "Using sys.path: {0}".format( sys.path )

	# important: import testsuite after modifing sys.path to load the correct module!
	import testsuite
	testsuite.main()

if __name__ == "__main__":
	main()
