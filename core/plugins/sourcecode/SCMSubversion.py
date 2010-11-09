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

from core.plugins.sourcecode.SourceCodeProvider import SourceCodeProvider
from core.Exceptions import ConfigurationError
from core.helpers.RunCommand import RunCommand
from core.actions.ShellCommandAction import ShellCommandAction
import time
from xml.dom import minidom
from core.plugins.sourcecode.RevisionInfo import RevisionInfo
import os
import tempfile
from core.helpers.FilesystemAccess import make_foldername_from_string
import sys

class SCMSubversion( SourceCodeProvider ):
	"""Subversion SCM Provider Class"""

	def __init__( self, name = None ):
		SourceCodeProvider.__init__( self, name )
		searchPaths = []
		if sys.platform == "win32":
			from core.helpers.RegistryHelper import getPathsFromRegistry
			keys = [ "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion"
				+ "\\Uninstall\\CollabNet Subversion Client\\UninstallString" ]
			searchPaths += getPathsFromRegistry( keys, ".." )
		self._setCommand( "svn", searchPaths )
		self.__revisionInfoCache = {} # key: revision, value: RevisionInfo instance


	def getIdentifier( self ):
		return 'svn'

	# TODO: Add support for fetching committer's email address from some lookup table
	def getRevisionInfo( self ):
		# check if specified revision is in cache. do not check for 'HEAD'
		if self.getRevision() in self.__revisionInfoCache:
			return self.__revisionInfoCache[self.getRevision()]

		info = RevisionInfo( "SvnRevisionInfo" )

		revisionParameter = ['-r', str( self.getRevision() )] if self.getRevision() else []
		cmd = [ self.getCommand(), '--non-interactive', 'log', '--xml', '--limit', '1', self.getUrl() ] + revisionParameter
		runner = RunCommand( cmd )
		runner.run()

		if runner.getReturnCode() == 0:
			xmldoc = minidom.parseString( runner.getStdOut() )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			assert len( logentries ) == 1
			results = parse_log_entry( logentries[0] )
			( info.committerName, info.commitMessage, info.revision, info.commitTime ) = results
		else:
			raise ConfigurationError( 'cannot get log for "{0}"'
				.format( self.getUrl() ) )

		# add to cache. do not add 'HEAD'
		if self.getRevision():
			self.__revisionInfoCache[self.getRevision()] = info

		return info

	def _getRevisionsSince( self, revision, cap = None ):
		"""Print revisions committed since the specified revision."""

		revision = int( revision )
		assert revision

		cmd = [ self.getCommand(), '--non-interactive', 'log', '--xml' ]
		if revision == 0:
			cmd.extend( ['--limit', '1' ] )
		cmd.extend( ['-rHEAD:{0}'.format( str( revision ).strip() ), self.getUrl() ] )
		runner = RunCommand( cmd, 3600 )
		runner.run()

		if runner.getReturnCode() == 0:
			revisions = []
			xmldoc = minidom.parseString( runner.getStdOut() )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			for entry in logentries:
				result = parse_log_entry( entry )
				if int( result[2] ) != revision: # svn log always spits out the last revision 
					revisions.append( ['C', int( result[2] ), self.getUrl() ] )
			return revisions
		elif runner.getTimedOut() == True:
			raise ConfigurationError( 'Getting svn log for "{0}" timed out.'.format( self.getUrl() ) )
		else:
			raise ConfigurationError( 'Getting svn log failed, is there no svn in the path?' )

	def _getCurrentRevision( self ):
		'''Return the identifier of the current revisions.'''
		cmd = [ self.getCommand(), '--non-interactive', 'log', '--xml', '--limit', '1', self.getUrl() ]
		runner = RunCommand( cmd )
		runner.run()

		if runner.getReturnCode() == 0:
			xmldoc = minidom.parseString( runner.getStdOut() )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			assert len( logentries ) == 1
			result = parse_log_entry( logentries[0] )
			return result[2]
		else:
			raise ConfigurationError( 'cannot get log for "{0}"'
				.format( self.getUrl() ) )

	def makeCheckoutStep( self ):
		"""Create steps to check out the source code"""
		assert self.getInstructions()
		step = self.getInstructions().getStep( 'project-checkout' )
		cmd = [ self.getCommand(), '--non-interactive', 'checkout',
			'-r{0}'.format( self.getRevision() or 'HEAD' ), self.getUrl(), '.' ]
		checkout = ShellCommandAction( cmd )
		checkout.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( checkout )
		return step

	def fetchRepositoryFolder( self, remotePath ):
		# FIXME Mike abstract cache location
		path = tempfile.mkdtemp( prefix = 'mom_buildscript-', suffix = make_foldername_from_string( self.getUrl() ) )
		if not self.getRevision():
			self.setRevision( 'HEAD' )
		location = self.getUrl()
		if remotePath:
			location += '/' + remotePath
		cmd = [ self.getCommand(), 'co', '-r', self.getRevision(), location ]
		runner = RunCommand( cmd )
		runner.setWorkingDir( path )
		runner.run()
		if runner.getReturnCode() == 0:
			localPath = os.path.join( path, remotePath )
			if os.path.exists( localPath ):
				return localPath
		raise ConfigurationError( 'The remote path {0} was not found in the repository at revision {1}'.format( 
				remotePath, self.getRevision() ) )

def parse_log_entry( logentry ):
	"""Parse one SVN log entry in XML format, return tuple (committer, message, revision, commitTime)"""
	revision = logentry.getAttribute( 'revision' )
	message = ''
	committer = ''
	commitTime = None

	for child in logentry.childNodes:
		if child.localName == 'author':
			committer = get_node_text( child )
		elif child.localName == 'date':
			commitTime = get_node_text( child )
		elif child.localName == 'msg':
			message = get_node_text( child )
		else:
			# this might be indentation whitespace
			pass

	# now turn commiTime into a Python datetime:
	commitTime = commitTime.split( '.' )[0] # strip microseconds
	commitTime = time.strptime( commitTime, '%Y-%m-%dT%H:%M:%S' )
	return ( committer, message, revision, time.strftime( "%Y-%m-%dT%H:%M", commitTime ) )

def get_node_text( node ):
	text = ''
	for sub in node.childNodes:
		text += sub.nodeValue
	return text
