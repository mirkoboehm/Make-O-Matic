#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from mom.apps.simple_ci.Master import Master
from mom.apps.simple_ci.Slave import Slave
import sys
from mom.core.helpers.GlobalMApp import mApp

def make_slave():
	# we have to copy some code here to instantiate the correct Simple CI instance (Master/Slave)
	for o in sys.argv[1:]:
		if o in ( "-s", "--slave" ):
			return True

	return False

if __name__ == "__main__":
	if make_slave():
		ci = Slave()
	else:
		ci = Master()

	# apply instance name if supplied
	if mApp().getParameters().getInstanceName():
		ci.setName( mApp().getParameters().getInstanceName() )

	ci.build()
