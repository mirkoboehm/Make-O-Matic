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
from core.helpers.GlobalMApp import mApp
from core.Exceptions import ConfigurationError
from core.helpers.StringResolver import StringResolver

class SettingResolver( StringResolver ):
	'''A SettingResolver returns the value of a setting at the time it is converted to a string.
	If required is true, a missing setting name or value causes a ConfigurationException to be raised.
	Otherwise, if no setting name is specified, it returns an empty string.
	If the setting is not defined, the default value is returned. 
	If no default value is defined, an empty string will be returned.'''

	def __init__( self, setting, required = False, defaultValue = None ):
		self.setSetting( setting )
		self.setDefaultValue( defaultValue )
		self.setRequired( required )

	def setSetting( self, name ):
		self.__setting = name

	def getSetting( self ):
		return self.__setting

	def setRequired( self, onOff ):
		self.__required = onOff

	def getRequired( self ):
		return self.__required

	def setDefaultValue( self, value ):
		self.__defaultValue = value

	def getDefaultValue( self ):
		return self.__defaultValue

	def __str__( self ):
		settings = mApp().getSettings()
		if self.getRequired():
			if not self.getSetting():
				raise ConfigurationError( 'The required setting name is not specified!' )
			if not settings.get( self.getSetting(), False ):
				raise ConfigurationError( 'The required value for setting {0} is undefined!'.format( self.getSetting() ) )
		value = settings.get( self.getSetting(), required = False, defaultValue = self.getDefaultValue() )
		if value:
			return '{0}'.format( value )
		else:
			return ''

