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
from core.executomat.Executomat import Executomat
from core.modules.reporters.StepReport import StepReport

class ExecutomatReport( object ):

	def __init__( self, executomat ):
		assert isinstance( executomat, Executomat )
		self.__executomat = executomat
		self.__summary = None
		self.__stepReports = []

	def getSummary( self ):
		return self.__summary

	def getStepReports( self ):
		return self.__stepReports

	def _getExecutomat( self ):
		return self.__executomat

	def prepare( self ):
		self.__summary = '{0} ({1})'\
			.format( self._getExecutomat().getName(),
					 self._getExecutomat().getTimeKeeper().deltaString() )
		for step in self._getExecutomat()._getSteps():
			report = StepReport( step )
			report.prepare()
			self.__stepReports.append( report )
