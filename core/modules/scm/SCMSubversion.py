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
from core.Exceptions import ConfigurationError
from core.helpers.RunCommand import RunCommand
from core.executomat.ShellCommandAction import ShellCommandAction
import time
from xml.dom import minidom
from core.helpers.GlobalMApp import mApp

class SCMSubversion( SourceCodeProvider ):

	"""Subversion SCM Provider Class"""

	def __init__( self, name = None ):
		SourceCodeProvider.__init__( self, name )

	def _getRevisionInfo( self ):
		"""Set __committer, __commitMessage, __commitTime and __revision"""
		raise NotImplementedError

	def _checkInstallation( self ):
		"""Check if this SCM can be used. Should check, for example, if the SCM is actually installed."""
		runner = RunCommand( ['svn', '--version'] )
		runner.run()
		if( runner.getReturnCode() != 0 ):
			raise ConfigurationError( "SCMSubversion::checkInstallation: svn not found." )
		else:
			lines = runner.getStdOut().decode().split( '\n' )
			self._setDescription( lines[0].rstrip() )
			mApp().debugN( self, 4, 'svn found: "{0}"'.format( self.getDescription() ) )

	def _getRevisionsSince( self, project, revision, cap = None ):
		"""Print revisions committed since the specified revision."""
		revision = int( revision )
		assert revision

		options = 'log --xml '
		if revision == 0:
			options += '--limit 1 '
		cmd = 'svn --non-interactive ' + options + '-rHEAD:' + str( revision ).strip() + ' ' + self.getUrl()
		runner = RunCommand( cmd, 3600 )
		runner.run()

		if runner.getReturnCode() == 0:
			output = runner.getStdOut().decode()
			revisions = []
			xmldoc = minidom.parseString( output )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			for entry in logentries:
				result = parseLogEntry( entry )
				if int( result[2] ) != revision: # svn log always spits out the last revision 
					revisions.append( ['C', int( result[2] ), project.getScmUrl() ] )
			return revisions
		elif runner.getTimedOut() == True:
			raise ConfigurationError( 'Getting svn log for "{0}" timed out.'.format( self.getUrl() ) )
		else:
			raise ConfigurationError( 'Getting svn log failed, is there no svn in the path?' )

	def _getCurrentRevision( self, project ):
		'''Return the identifier of the current revisions.'''
		cmd = [ 'svn', '--non-interactive', 'log', '--xml', '--limit 1', self.getUrl() ]
		runner = RunCommand( project, cmd )
		runner.run()

		if runner.getReturnCode() == 0:
			xmldoc = minidom.parseString( runner.getStdOut() )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			assert len( logentries ) == 1
			result = parseLogEntry( logentries[0] )
			return result[2]
		else:
			raise ConfigurationError( 'cannot get log for "{0}"'
				.format( self.getUrl() ) )

	def makeCheckoutStep( self ):
		"""Create steps to check out the source code"""
		assert self.getInstructions()
		step = self.getInstructions().getStep( 'project-checkout' )
		cmd = 'svn --non-interactive checkout -r"{0}" {1} .'.format( 
			self.getRevision() or 'HEAD',
			self.getUrl() )
		checkout = ShellCommandAction( cmd )
		checkout.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( checkout )
		return step


def parseLogEntry( logentry ):
	"""Parse one SVN log entry in XML format, return tuple (committer, message, revision, commitTime)"""
	revision = logentry.getAttribute( 'revision' )
	message = ''
	committer = ''
	commitTime = None
	for child in logentry.childNodes:
		if child.localName == 'author':
			committer = getNodeText( child )
		elif child.localName == 'date':
			commitTime = getNodeText( child )
		elif child.localName == 'msg':
			message = getNodeText( child )
		else:
			# this might be indentation whitespace
			pass
	# now turn commiTime into a Python datetime:
	commitTime = commitTime.split( '.' )[0] # strip microseconds
	commitTime = time.strptime( commitTime, '%Y-%m-%dT%H:%M:%S' )
	return ( committer, message, revision, commitTime )

def getNodeText( node ):
	text = ''
	for sub in node.childNodes:
		text += sub.nodeValue
	return text
