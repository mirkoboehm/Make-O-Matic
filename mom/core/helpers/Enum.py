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

class Enum( object ):
	_Descriptions = [] # overwrite in subclass!

	@classmethod
	def getKey( cls, enumValue ):
		l = [key for key, val in cls.__dict__.items() if val == enumValue]
		if len( l ) > 0:
			return l[0]
		else:
			return None

	@classmethod
	def getDescriptionFromKey( cls, enumKeyString ):
		l = [val for key, val in cls.__dict__.items() if key == enumKeyString]
		if len( l ) > 0:
			return cls.getDescription( l[0] )
		else:
			return None

	@classmethod
	def getDescription( cls, enumValue ):
		try:
			return cls._Descriptions[enumValue]
		except KeyError, TypeError:
			return "N/A"
