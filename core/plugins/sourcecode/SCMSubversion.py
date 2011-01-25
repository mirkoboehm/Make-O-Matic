# This file is part of Make-O-Matic.
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mirko Boehm <mirko.boehm@kdab.com>
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
from buildcontrol.common.BuildInfo import BuildInfo
from core.Settings import Settings
from core.helpers.GlobalMApp import mApp
from datetime import datetime
import calendar
from core.helpers.TimeUtils import formatted_time

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
		self._setCommand( "svn" )
		self._setCommandSearchPaths( searchPaths )
		self.__revisionInfoCache = {} # key: revision, value: RevisionInfo instance
		self.__rootTrunk = False

	def setRootTrunk( self, rootTrunk ):
		self.__rootTrunk = rootTrunk

	def rootIsTrunk( self ):
		return self.__rootTrunk

	def __getRootUrl( self ):
		return super( SCMSubversion, self ).getUrl()

	def getUrl( self ):
		# TODO Work out sensible ordering here or fail if we have more than one of these parameters
		url = SourceCodeProvider.getUrl( self )
		if self.getTag():
			return url + '/tags/' + self.getTag()
		elif self.getBranch():
			return url + '/branches/' + self.getBranch()
		elif not self.rootIsTrunk():
			return url + '/trunk'

		return url

	def getIdentifier( self ):
		return 'svn'

	def getRevisionInfo( self ):
		# check if specified revision is in cache. do not check for 'HEAD'
		if self.getRevision() in self.__revisionInfoCache:
			return self.__revisionInfoCache[self.getRevision()]

		info = RevisionInfo( "SvnRevisionInfo" )

		revisionParameter = ['-r', str( self.getRevision() )] if self.getRevision() else []
		cmd = [ self.getCommand(), '--non-interactive', 'log', '--xml', '--limit', '1', self.getUrl() ] + revisionParameter
		runner = RunCommand( cmd, searchPaths = self.getCommandSearchPaths() )
		runner.run()

		if runner.getReturnCode() == 0:
			xmldoc = minidom.parseString( runner.getStdOut() )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			assert len( logentries ) == 1
			results = parse_log_entry( logentries[0] )
			( info.committerName, info.commitMessage, info.revision, info.commitTime, info.commitTimeReadable ) = results

			if self.getSCMUidMapper():
				email = self.getSCMUidMapper().getEmail( info.committerName )
				mApp().debugN( self, 5, "E-Mail address for {0} from SCM uid mapper: {1}".format( info.committerName, email ) )
				info.committerEmail = email

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
		runner = RunCommand( cmd, 3600, searchPaths = self.getCommandSearchPaths() )
		runner.run()

		if runner.getReturnCode() == 0:
			revisions = []
			xmldoc = minidom.parseString( runner.getStdOut() )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			for entry in logentries:
				result = parse_log_entry( entry )
				if int( result[2] ) != revision: # svn log always spits out the last revision
					info = BuildInfo()
					info.setProjectName( mApp().getSettings().get( Settings.ScriptBuildName ) )
					info.setBuildType( 'C' ) # the default, FIXME add classifiers
					info.setRevision( int( result[2] ) )
					info.setUrl( self.__getRootUrl() )
					# FIXME only trunk is supported this way
					info.setBranch( None )
					info.setTag( None )
					revisions.append( info )
			if cap:
				return revisions[-cap:]
			else:
				return revisions
		elif runner.getTimedOut() == True:
			raise ConfigurationError( 'Getting svn log for "{0}" timed out.'.format( self.getUrl() ) )
		else:
			raise ConfigurationError( 'Getting svn log failed, is there no svn in the path?' )

	def _getCurrentRevision( self ):
		'''Return the identifier of the current revisions.'''
		cmd = [ self.getCommand(), '--non-interactive', 'log', '--xml', '--limit', '1', self.getUrl() ]
		runner = RunCommand( cmd, searchPaths = self.getCommandSearchPaths() )
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
		step = self.getInstructions().getStep( 'checkout' )
		cmd = [ self.getCommand(), '--non-interactive', 'checkout',
			'-r{0}'.format( self.getRevision() or 'HEAD' ), self.getUrl(), '.' ]
		checkout = ShellCommandAction( cmd, searchPaths = self.getCommandSearchPaths() )
		checkout.setWorkingDirectory( self.getSrcDir() )
		step.addMainAction( checkout )

	def fetchRepositoryFolder( self, remotePath ):
		# FIXME Mike abstract cache location
		path = tempfile.mkdtemp( prefix = 'mom_buildscript-', suffix = make_foldername_from_string( self.getUrl() ) )
		if not self.getRevision():
			self.setRevision( 'HEAD' )
		location = self.getUrl()
		if remotePath:
			location += '/' + remotePath
		cmd = [ self.getCommand(), 'co', '-r', self.getRevision(), location ]
		runner = RunCommand( cmd, searchPaths = self.getCommandSearchPaths() )
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
			message = get_node_text( child ).rstrip()
		else:
			# this might be indentation whitespace
			pass

	# now turn commiTime into a Python datetime:
	timeString = commitTime.split( '.' )[0] # strip microseconds
	timeTuple = time.strptime( timeString, '%Y-%m-%dT%H:%M:%S' )
	return ( committer, message, revision, calendar.timegm( timeTuple ), formatted_time( datetime( *timeTuple[0:6] ) ) )

def get_node_text( node ):
	text = ''
	for sub in node.childNodes:
		text += sub.nodeValue
	return text
