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
from core.helpers.RevisionInfo import RevisionInfo
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
import re
from core.Defaults import Defaults

if sys.platform == "win32":
	from core.helpers.RegistryHelper import getPathsFromRegistry

class SCMSubversion( SourceCodeProvider ):
	"""Subversion SCM Provider Class"""

	def __init__( self, name = None ):
		SourceCodeProvider.__init__( self, name )
		searchPaths = []
		if sys.platform == "win32":
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

	def _retrieveRevisionInfo( self ):
		# check if specified revision is in cache. do not check for 'HEAD'
		if self.getRevision() in self.__revisionInfoCache:
			return self.__revisionInfoCache[self.getRevision()]

		info = RevisionInfo( "SvnRevisionInfo" )

		revisionParameter = ['-r', str( self.getRevision() )] if self.getRevision() else []
		cmd = [ self.getCommand(), '--non-interactive', 'log', '--xml', '--limit', '1', self.getUrl() ] + revisionParameter
		runner = RunCommand( cmd, searchPaths = self.getCommandSearchPaths() )
		runner.run()

		if runner.getReturnCode() == 0:
			xmldoc = minidom.parseString( runner.getStdOut().encode( "utf-8" ) )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			assert len( logentries ) == 1
			results = parse_log_entry( logentries[0] )
			( info.committerName, info.commitMessage, info.revision, info.commitTime, info.commitTimeReadable ) = results
			info.shortRevision = info.revision

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
		xmlLog = self.__getXmlSvnLog( self.getUrl(), revision, cap )
		buildInfos = self.__getXmlSvnLogEntries( xmlLog, revision, cap )
		return buildInfos

	def _getRevisionsSinceAllBranches( self, revision, cap = None ):
		"""Return revisions committed since the specified revision, for all branches."""
		mApp().debugN( self, 3, 'Retrieving revisions for all branches since {0}'.format( revision ) )
		revision = int( revision )
		assert revision
		url = self.__getRootUrl()
		xmlLog = self.__getXmlSvnLog( url, revision, cap )
		buildInfos = self.__getXmlSvnLogEntries( xmlLog, revision, cap )
		locationMap = mApp().getSettings().get( Defaults.SCMSvnLocationBuildTypeMap, True )
		branchBuildInfos = []
		for buildInfo in buildInfos:
			diff = self.__getSummarizedDiffForRevision( url, buildInfo.getRevision() )
			branchBuildInfos.extend( self._splitIntoBuildInfos( buildInfo, diff, locationMap ) )
		return branchBuildInfos

	def __getXmlSvnLog( self, url, revision, cap ):
		cmd = [ self.getCommand(), '--non-interactive', 'log', '--xml' ]
		if revision == 0:
			cmd.extend( ['--limit', '1' ] )
		cmd.extend( ['-rHEAD:{0}'.format( str( revision ).strip() ), url ] )
		runner = RunCommand( cmd, 3600, searchPaths = self.getCommandSearchPaths() )
		runner.run()
		if runner.getReturnCode() == 0:
			return minidom.parseString( runner.getStdOut().encode( "utf-8" ) )
		elif runner.getTimedOut() == True:
			raise ConfigurationError( 'Getting svn log for "{0}" timed out.'.format( self.getUrl() ) )
		else:
			msg = runner.getStdErr() or ""
			msg = msg.strip()
			raise ConfigurationError( 'Getting svn log failed: "{0}"'.format( msg ) )

	def __getXmlSvnLogEntries( self, xmlLog, startRevision, cap ):
		revisions = []
		logentries = xmlLog.getElementsByTagName( 'logentry' )
		for entry in logentries:
			result = parse_log_entry( entry )
			if int( result[2] ) != startRevision: # svn log always spits out the last revision
				info = BuildInfo()
				info.setProjectName( mApp().getSettings().get( Settings.ScriptBuildName ) )
				info.setBuildType( 'C' )
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

	def _splitIntoBuildInfos( self, buildInfo, diff, locationBuildTypeMapping ):
		changes = {}
		url = buildInfo.getUrl()
		branchPrefix = mApp().getSettings().get( Settings.SCMSvnBranchPrefix )
		tagPrefix = mApp().getSettings().get( Settings.SCMSvnTagPrefix )
		for line in diff or []:
			line = line.strip()
			if not re.match( '^[A-Z]+\s+', line ):
				continue
			strippedLocation = re.sub( '^[A-Z]+\s+', '', line ).strip()
			location = strippedLocation[len( url ):] # remove URL
			for match, locationType, buildType in locationBuildTypeMapping:
				if not location.startswith( match ):
					continue
				info = BuildInfo()
				info.setProjectName( mApp().getSettings().get( Settings.ScriptBuildName ) )
				info.setBuildType( buildType )
				info.setRevision( buildInfo.getRevision() )
				info.setUrl( self.__getRootUrl() )

				def getBranchName( paths, prefix, match ):
					pathParts = paths.split( '/' )
					prefixParts = prefix.split( '/' )
					matchParts = match.split( '/' )
					itemsToInclude = len( matchParts ) - len( prefixParts ) + 1 # plus branch name
					if len( pathParts ) <= len( matchParts ):
						return None # ignore lines like 'A	 branches' in old diffs 
					firstIndex = len( prefixParts )
					branchNameParts = pathParts[ firstIndex : firstIndex + itemsToInclude ]
					branchName = '/'.join( branchNameParts )
					return branchName

				if locationType == Defaults.BranchType_Master:
					key = self.__getRootUrl() + '/MASTER' # the actual key does not matter, as long as it is in the map
				elif locationType == Defaults.BranchType_Branch:
					if not match.startswith( branchPrefix ):
						details = 'A location mapping of the branch type needs to be located in the branches folder ' \
							+ 'in the Subversion.repository'
						raise ConfigurationError( 
							'The Subversion location mapping "{0}" does not begin with the configured branch prefix "{1}".'
							.format( match, branchPrefix ), details )
					branchName = getBranchName( location, branchPrefix, match )
					if not branchName:
						continue # this line changed the branches folders, nothing else
					info.setBranch( branchName )
					key = '/'.join( [ self.__getRootUrl(), branchPrefix, branchName ] )
				elif locationType == Defaults.BranchType_Tag:
					if not match.startswith( tagPrefix ):
						details = 'A location mapping of the tag type needs to be located in the tags folder ' \
							+ 'in the Subversion.repository'
						raise ConfigurationError( 
							'The Subversion location mapping "{0}" does not begin with the configured tag prefix "{1}".'
							.format( match, branchPrefix ), details )
					branchName = getBranchName( location, tagPrefix, match )
					if not branchName:
						continue # this line changed the tags folders, nothing else
					info.setTag( branchName )
					key = '/'.join( [ self.__getRootUrl(), tagPrefix, branchName ] )
				if not changes.has_key( key ):
					mApp().debugN( self, 2, 'New build information for revision {0}, {1}'.format( buildInfo.getRevision(), key ) )
					self._applyBranchnameBuildtypeMapping( locationType, info )
					changes[key] = info
				break
		return changes.values()

	def _applyBranchnameBuildtypeMapping( self, branchType, buildInfo ):
		mappings = mApp().getSettings().get( Settings.SCMSvnBranchNameBuildTypeMap )
		if branchType == Defaults.BranchType_Master:
			# patterns are only applied to branches and tags:
			return
		for mappingBranchType, rx, buildType in mappings:
			if branchType != mappingBranchType:
				# do not apply this mapping to this buildInfo
				continue
			name = buildInfo.getBranch() if branchType == Defaults.BranchType_Branch else buildInfo.getTag()
			if re.match( rx, name ):
				mApp().debugN( self, 2, 'Setting the build type to {0} for revision {1}, because the branch name matches {2}' \
					.format( buildType, buildInfo.getRevision(), rx ) )
				buildInfo.setBuildType( buildType )

	def __getSummarizedDiffForRevision( self, url, revision ):
		previous = revision - 1
		cmd = [ self.getCommand(), 'diff', '--summarize', '-r', str( previous ) + ':' + str( revision ), url ]
		runner = RunCommand( cmd, 3600, searchPaths = self.getCommandSearchPaths() )
		runner.run()
		if runner.getReturnCode() != 0:
			# maybe the location did not exist earlier on: 
			mApp().debugN( self, 2, 'cannot retrieve summarized diff for revision "{0}"'.format( revision ) )
			return None
		else:
			return runner.getStdOut().encode( "utf-8" ).split( '\n' )

	def _getCurrentRevision( self ):
		'''Return the identifier of the current revisions.'''
		return self.__getCurrentRevisionOfUrl( self.getUrl() )

	def _getCurrentRevisionAllBranches( self ):
		'''Return the identifier of the current revisions for all branches.'''
		return self.__getCurrentRevisionOfUrl( self.__getRootUrl() )

	def __getCurrentRevisionOfUrl( self, url ):
		cmd = [ self.getCommand(), '--non-interactive', 'log', '--xml', '--limit', '1', url ]
		runner = RunCommand( cmd, searchPaths = self.getCommandSearchPaths() )
		runner.run()

		if runner.getReturnCode() == 0:
			xmldoc = minidom.parseString( runner.getStdOut().encode( "utf-8" ) )
			logentries = xmldoc.getElementsByTagName( 'logentry' )
			assert len( logentries ) == 1
			result = parse_log_entry( logentries[0] )
			return result[2]
		else:
			raise ConfigurationError( 'cannot get log for "{0}"'.format( url ) )

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
				return localPath, [ path ]
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
