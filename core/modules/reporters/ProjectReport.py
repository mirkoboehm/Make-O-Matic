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
from core.modules.reporters.ExecutomatReport import ExecutomatReport

class ProjectReport( object ):

	def __init__( self, project ):
		from core.Project import Project
		assert isinstance( project, Project )
		self.__project = project
		self.__executomatReport = ExecutomatReport( project._getExecutomat() )
		self.__summary = None

	def getProject( self ):
		return self.__project

	def getSummary( self ):
		return self.__summary

	def getReport( self ):
		report = '{0}\n'''.format( self.getSummary() )

		for stepReport in self.__executomatReport.getStepReports():
			report += '{0}: {1}\n'.format( stepReport.getStep().getName(), stepReport.getSummary() )
			if stepReport.getHasDetails():
				report += '   *** {0} ***\n'.format( stepReport.getDescription() )
		return report

	def prepare( self ):
		self.__summary = '''\
Build report for "{0}"
Total build time: {1}
'''.format( self.getProject().getName(), self.getProject().getTimeKeeper().deltaString() )
		self.__executomatReport.prepare()

