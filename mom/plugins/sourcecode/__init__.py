# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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
from mom.plugins.sourcecode.SCMGit import SCMGit
from mom.plugins.sourcecode.SCMSubversion import SCMSubversion
from mom.plugins.sourcecode.LocalSourceDirectory import LocalSourceDirectory
from mom.core.Exceptions import ConfigurationError
import re

def getScm( url, name = None ):
	'''Create a SourceCodeProvider object according to the specified URL.
	The SCM type will be auto-detected or may be prefixed with an identifier
	to force it to get a certain type of provider. Examples:
	'svn:svn+ssh://svn.kde.org/home/kde/abcde' describes a Subversion repository.
	'git://github.com/KDAB/Make-O-Matic.git' auto-detects a GIT repository.
	'''
	scmProviders = {}
	for scm in [ SCMGit( name ), SCMSubversion( name ), LocalSourceDirectory( name ) ]:
		scmProviders[scm.getIdentifier()] = scm

	scmRegex = '(' + '|'.join( scmProviders ) + ')'
	scmIdentifierRegex = scmRegex + ':(?!//)'
	# Check for manually specified identifier first
	# Don't match e.g. git://
	match = re.match( scmIdentifierRegex, url )
	if match:
		# Get out the URL without the identifier prefix
		_, _, url = url.partition( match.group( 0 ) )
	else:
		# If we can't find the identifier, look for it anywhere in the URL
		match = re.search( scmRegex , url )

	if match:
		try:
			scm = scmProviders[ match.group( 1 ) ]
			scm.setUrl( url )
			return scm
		except IndexError, KeyError:
			pass

	raise ConfigurationError( 'Cannot create source code provider for URL "{0}", unknown implementation'.format( url ) )
