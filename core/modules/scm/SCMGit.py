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
from core.modules.SourceCodeProvider import SourceCodeProvider
from core.Exceptions import AbstractMethodCalledError, ConfigurationError
from core.helpers.RunCommand import RunCommand

class SCMGit( SourceCodeProvider ):
	"""Git SCM Provider Class"""

	def __init__( self, name = None ):
		SourceCodeProvider.__init__( self, name )

	def _getRevisionInfo( self ):
		"""Set __committer, __commitMessage, __commitTime and __revision"""
		raise AbstractMethodCalledError

	def _checkInstallation( self, project ):
		"""Check if this SCM can be used. Should check, for example, if the SCM is actually installed."""
		# c				"""Check if this SCM can be used. Should check, for example, if the SCM is actually installed."""
		assert project
		runner = RunCommand( project, 'git --version' )
		runner.run()
		if( runner.getReturnCode() != 0 ):
			raise ConfigurationError( "SCMGit::checkInstallation: git not found." )
		else:
			lines = runner.getStdOut().decode().split( '\n' )
			self._setDescription( lines[0].rstrip() )
			project.debugN( self, 2, 'git found: "{0}"'.format( self.getDescription() ) )
