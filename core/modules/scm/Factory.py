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
import re
from core.Exceptions import ConfigurationError
from core.modules.scm.SCMGit import SCMGit
from core.modules.scm.SCMSubversion import SCMSubversion
from core.MObject import MObject
from core.helpers.GlobalMApp import mApp

class SourceCodeProviderFactory( MObject ):

	def __init__( self, name = None ):
		MObject.__init__( self, name )

	def parseDescription( self, description ):
		# extract implementation identifier and SCM location part out of the description:
		pattern = '^(.+?):(.*)$'
		patternObj = re.compile( pattern )
		groups = patternObj.search( description )
		if not groups or len( groups.groups() ) != 2:
			raise ConfigurationError( 'Cannot parse source code provider description "{0}" '.format( description ) )
		implementation, location = groups.groups()
		return implementation, location

	def makeScmForImplementationIdentifier( self, implementation ):
		# the factory part (not super-sophisticated):
		scm = None
		if implementation == 'git':
			scm = SCMGit()
		elif implementation == 'svn':
			scm = SCMSubversion()
		else:
			raise ConfigurationError( 'Cannot create source code provider for identifier "{0}", unknown implementation'
									.format( implementation ) )
		mApp().debugN( self, 2, 'created "{0}" source code provider'.format( scm.getName() ) )
		return scm

	def makeScmImplementation( self, description ):
		'''Create a SourceCodeProvider object according to the specified description.
		The description consists of an implementation identifier, and an implementation
		specific location. Examples: 
		'svn:svn+ssh://svn.kde.org/home/kde/abcde' describes a Subversion repository.
		'git:git://github.com/mirkoboehm/Make-O-Matic.git' describes a GIT repository.
		'localdir:/home/dude/myproject/src' describes a local directory to be used.
		'''
		implementation, location = self.parseDescription( description )
		mApp().debugN( self, 3, 'implementation identifier: "{0}", location: "{1}"'.format( implementation, location ) )
		scm = self.makeScmForImplementationIdentifier( implementation )
		scm.setUrl( location )
		return scm

