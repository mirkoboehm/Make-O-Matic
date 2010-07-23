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
from core.executomat.Step import Step

class StepReport( object ):
	"""Generate a human readable report about the step execution."""

	def __init__( self, step ):
		assert isinstance( step, Step )
		self.__step = step
		self.__hasDetails = False
		self.__summary = None
		self.__description = None

	def getStep( self ):
		return self.__step

	def _setDescription( self, description ):
		self.__description = description

	def getDescription( self ):
		return self.__description

	def _setSummary( self, summary ):
		self.__summary = summary

	def getSummary( self ):
		return self.__summary

	def _setHasDetails( self, does ):
		self.__hasDetails = does

	def getHasDetails( self ):
		return self.__hasDetails

	def prepare( self ):
		if not self.getStep().getEnabled():
			self._setDescription( 'disabled' )
			self._setSummary( 'disabled' )
			return
		workSet = ( ['precmds', self.getStep().getPreActions() ],
					['maincmds', self.getStep().getMainActions() ],
					['postcmds', self.getStep().getPostActions() ] )
		notRun = True
		failed = False
		results = []
		empty = True
		for phase in workSet:
			description = ''
			description = 'none'
			for action in phase[1]:
				self._setHasDetails( True )
				empty = False
				if not action.wasStarted():
					description = 'skipped'
					break
# FIXME Mirko timeout is not a generic concept!
#					elif action.timedOut():
#						description = 'timeout (failed)'
#						failed = True
#						notRun = False
#						break
				elif action.getResult() != 0:
					description = 'failed'
					failed = True
					notRun = False
					break
				else: # success
					notRun = False
					description = 'ok'
			results.append( '{0}: {1}'.format( phase[0], description ) )
		result = ', '.join( results )
		if empty:
			self._setSummary( 'empty' )
		elif notRun:
			self._setSummary( 'SKIPPED' )
		elif failed:
			self._setSummary( 'FAILED ({0})'.format( self.getStep().getTimeKeeper().deltaString() ) )
		else:
			self._setSummary( 'success ({0})'.format( self.getStep().getTimeKeeper().deltaString() ) )
		self._setDescription( result )
