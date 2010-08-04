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
from core.helpers.TypeCheckers import check_for_nonempty_string
from core.helpers.GlobalMApp import mApp
from core.Exceptions import MomError, MomException
import sys

# FIXME this might better be a member function of MAplication
def checkMinimumMomVersion( minimumMomVersion ):
	'''Check if this make-o-matic copy is recent enough for this build script.
	If not, the function does not return, but instead exits the script with an error Message.'''
	if not minimumMomVersion:
		mApp().debug( mApp(), 'No minimum make-o-matic version specified.' )
		return
	try:
		check_for_nonempty_string( minimumMomVersion, 'minimumMomVersion needs to be a version string like "0.5.5"' )
		minVersion = minimumMomVersion.split( '.' )
		version = mApp().getMomVersion().split( '.' )
		if len( version ) != 3 or len( minVersion ) != len( version ) :
			raise MomError( 'Version descriptions must be strings of 3 integer numbers, like "0.5.5"' )
		for position in range( len( version ) ):
			try:
				element = int( version[position] )
				minElement = int( minVersion[position] )
				if element < minElement:
					raise MomError( 'This build script requires make-o-matic ' + minimumMomVersion
										 + ', but this is only make-o-matic ' + mApp().getMomVersion() + ', aborting.' )
			except ValueError:
				raise MomError( 'Version descriptions must be strings of integer numbers, like "0.5.5"' )
	except MomException as  e:
		mApp().message( mApp(), e.value )
		sys.exit( 1 )
