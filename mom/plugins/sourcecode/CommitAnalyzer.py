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

from mom.core.Plugin import Plugin
from mom.core.Exceptions import AbortBuildException

class CommitAnalyzer( Plugin ):
	"""This plugin analyzes the to-be-built commit of the project

	Currently handled keywords in commit messages:
	* AUTOBUILD_IGNORE: Abort build if specified
	"""

	def setup( self ):
		# use setup phase, revision info should be fetched at this point
		project = self.getInstructions().getProject()
		scm = project.getScm()
		revisionInfo = scm.getRevisionInfo()

		self._parse( revisionInfo )

	def _parse( self, revisionInfo ):
		"""Parse revision info object, call sub-handlers"""

		message = revisionInfo.commitMessage

		for line in message.splitlines():
			if line.startswith( "AUTOBUILD_IGNORE" ):
				self._handleIgnore( revisionInfo )

	def _handleIgnore( self, revisionInfo ):
		raise AbortBuildException( "AUTOBUILD_IGNORE specified in commit message" )
