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
import os

def addToPathCollection( pathVariable, element, order = 'append' ):
	# pathVariable is the name of the environment variable
	# safely get the existing setting:
	# try if the given path exists
	#if 'packages' or 'Qt' in element and os.path.exists(element) == False:
	#raise EnvironmentError('FatalError : ' + element + ' : does not exist')
	variable = ''
	try:
		variable = os.environ[pathVariable]
	except:
		pass
	# prune it and split it up (not too aggressively): 
	if variable[-1:] == os.pathsep:
		variable = variable[:-1]
	elements = variable.split( os.pathsep )
	if element not in elements:
		if order == 'prepend':
			elements = [ element ] + elements
		else:
			elements.append( element )

	def WhiteSpaceFilter( x ): return x.strip() != ''
	elements = filter( WhiteSpaceFilter, elements )

	result = os.pathsep.join( elements )
	os.environ[pathVariable] = result
