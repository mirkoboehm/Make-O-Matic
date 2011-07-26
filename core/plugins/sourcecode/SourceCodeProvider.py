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

from core.Exceptions import MomError, ConfigurationError
from core.helpers.TypeCheckers import check_for_path
from core.Plugin import Plugin
from core.helpers.XmlUtils import create_child_node
from core.helpers.XmlReportConverter import ReportFormat
from core.helpers.SCMUidMapper import SCMUidMapper
from buildcontrol.common.BuildInfo import BuildInfo
from core.helpers.GlobalMApp import mApp
from core.Settings import Settings
import datetime

class SourceCodeProvider( Plugin ):

	DefaultUidMappings = "defaultuidmappings"

	def __init__( self, name = None ):
		Plugin.__init__( self, name )
		self.__url = None
		self.__revision = None
		self.__branch = None
		self.__tag = None
		self.__srcDir = None
		self.__mapper = SCMUidMapper( self )
		self.__parseBranchCommits = False
		self.__revisionInfo = None

	def getObjectStatus( self ):
		return self.getUrl()

	def getIdentifier( self ):
		raise NotImplementedError

	def setUrl( self, url ):
		self.__url = url.rstrip( '/' )

	def getUrl( self ):
		return self.__url

	def setSrcDir( self, srcDir ):
		check_for_path( srcDir, 'The course folder needs to be a non-empty string!' )
		self.__srcDir = srcDir

	def getSrcDir( self ):
		return self.__srcDir

	def setRevision( self, revision ):
		self.__revision = revision

	def getRevision( self ):
		return self.__revision

	def setBranch( self, branch ):
		self.__branch = branch

	def getBranch( self ):
		return self.__branch

	def getSCMUidMapper( self ):
		return self.__mapper

	def setTag( self, tag ):
		self.__tag = tag

	def getTag( self ):
		return self.__tag

	def doParseBranchCommits( self ):
		return self.__parseBranchCommits

	def setParseBranchCommits( self, onOff ):
		self.__parseBranchCommits = onOff

	def getPluginType( self ):
		return "scm"

	def getRevisionInfo( self ):
		"""Returns a RevisionInfo object"""
		if not self.__revisionInfo:
			info = self._retrieveRevisionInfo()
			if not info or not info.isValid():
				raise ConfigurationError( 'Unable to retrieve revision information. Is the SCM reachable?' )

			self.__revisionInfo = info
			mApp().getSettings().set( Settings.ProjectRevision, info.revision )
			mApp().getSettings().set( Settings.ProjectShortRevision, info.shortRevision )
			dateAndRevision = 'Local-Build-HEAD'
			if info.commitTime:
				commitTime = datetime.datetime.utcfromtimestamp( int( info.commitTime ) )
				dateAndRevision = commitTime.strftime( '%Y-%m-%d_%H-%M_{0:_>8}' ).format( info.shortRevision )
			mApp().getSettings().set( Settings.ProjectRevisionWithTime, dateAndRevision )
		return self.__revisionInfo

	def _resetRevisionInfo( self ):
		'''This should only be necessary in special cases, like tests.'''
		self.__revisionInfo = None

	def _retrieveRevisionInfo( self ):
		raise NotImplementedError

	def _handlePrintCommands( self, command, options ):
		commands = {
			'revisions-since' : [ self.printRevisionsSince, 'print revisions committed since specified revision' ],
			'current-revision': [ self.printCurrentRevision, 'print current revision' ]
		}
		if command in commands:
			method = commands[ command ][0]
			print( method( options ) )
		else:
			text = 'Unknown command "{0}" for run mode "print". Known commands are:'.format( command )
			for cmd in commands:
				text += '\n   {0}: {1}'.format( cmd, commands[ cmd ][1] )
			raise ConfigurationError( text )


	def printRevisionsSince( self, options ):
		"""Print revisions committed since the specified buildInfo."""
		if not options:
			raise MomError( 'No buildInfo specified to start with!' )
		if len( options ) > 2:
			raise MomError( 'Error, extra options. Specify buildInfo and optionally the maximum number of buildInfos to print.' )
		buildInfo = options[0]
		cap = None
		if len( options ) == 2:
			cap = int( options[1] )

		buildInfos = self._getRevisionsSinceAllBranches( buildInfo, cap ) \
			if self.doParseBranchCommits() \
			else self._getRevisionsSince( buildInfo, cap )
		lines = []
		for buildInfo in buildInfos:
			assert isinstance( buildInfo, BuildInfo )
			line = buildInfo.printableRepresentation()
			lines.append( line )
		return '\n'.join( lines )

	def _getRevisionsSinceAllBranches( self, revision, cap = None ):
		"""Return revisions committed since the specified revision, for all branches."""
		raise NotImplementedError

	def _getRevisionsSince( self, revision, cap = None ):
		"""Return revisions committed since the specified revision for the selected branch."""
		raise NotImplementedError

	def printCurrentRevision( self, options ):
		"""Print current (most recent) revision."""
		if options:
			raise MomError( 'print current-revision does not understand any extra options!' )

		revision = self._getCurrentRevisionAllBranches() \
			if self.doParseBranchCommits() \
			else self._getCurrentRevision()
		return revision

	def _getCurrentRevisionAllBranches( self ):
		'''Return the identifier of the current revisions for all branches.'''
		raise NotImplementedError

	def _getCurrentRevision( self ):
		'''Return the identifier of the current revisions for the selected branch.'''
		raise NotImplementedError

	def makeCheckoutStep( self ):
		"""Create steps to check out the source code"""
		raise NotImplementedError()

	def makeExportStep( self, targetDir ):
		"""Create a Step that will export the source code to the target directory."""
		raise NotImplementedError()

	def prepare( self ):
		# add mappings set from config files
		mappings = self.getSetting( self.DefaultUidMappings, False ) or []
		mApp().debugN( self, 5, "Adding uid mappings for source code provider. Mappings found: {0}".format( len( mappings ) ) )
		for mapping in mappings:
			self.getSCMUidMapper().addMapping( mapping )
		# We need to check for the SCM here to error if the SCM can't be found for checkout.
		if self.getCommand():
			self.resolveCommand()
		# save tag or branch to the settings, so that the values can be used later in other modules:
		settings = mApp().getSettings()
		name = ''
		if self.getBranch():
			name = str( self.getBranch() )
			settings.set( Settings.SourceCodeProviderBranchPrefix, 'branches' )
		elif self.getTag():
			name = str( self.getTag() )
			settings.set( Settings.SourceCodeProviderBranchPrefix, 'tags' )
		else:
			name = 'master'
			settings.set( Settings.SourceCodeProviderBranchPrefix, '' )
		settings.set( Settings.SourceCodeProviderVersionName, name )

	def preFlightCheck( self ):
		mode = mApp().getSettings().get( Settings.ScriptRunMode )
		if mode in ( Settings.RunMode_Build, Settings.RunMode_Print ):
			self.getRevisionInfo()

	def setup( self ):
		"""Setup is called after the build steps have been generated, and the command line 
		options have been applied to them. It can be used to insert actions into the build
		steps, for example."""
		self.makeCheckoutStep()

	def getXslTemplates( self ):
		return { ReportFormat.HTML:
			"""
			Revision: <xsl:value-of select="pluginInfo/@revision"/><br/>
			Committer: <xsl:value-of select="pluginInfo/@committerName"/> &lt;<xsl:value-of select="pluginInfo/@committerEmail"/>&gt;<br/>
			Time: <xsl:value-of select="pluginInfo/@commitTimeReadable"/><br/>
			Message: <pre><xsl:value-of select="pluginInfo/commitMessage"/></pre>
			""" }

	def getXmlTemplate( self, element, wrapper ):
		out = []

		out += wrapper.wrap( "Revision: {0}".format( element.attrib["revision"] ) )
		out += wrapper.wrap( "Committer: {0} <{1}>".format( element.attrib["committerName"], element.attrib["committerEmail"] ) )
		out += wrapper.wrap( "Time: {0}".format( element.attrib["commitTimeReadable"] ) )

		out += wrapper.wrap( "Commit message following:" )
		wrapper.indent()
		out += wrapper.wrapMultiLine( element.find( "commitMessage" ).text )
		wrapper.dedent()

		return out

	def createXmlNode( self, document ):
		node = super( SourceCodeProvider, self ).createXmlNode( document )

		pluginInfo = document.createElement( "pluginInfo" )
		info = self.getRevisionInfo()
		pluginInfo.attributes["revision"] = unicode( info.revision )
		pluginInfo.attributes["committerName"] = unicode( info.committerName )
		pluginInfo.attributes["committerEmail"] = unicode( info.committerEmail )
		pluginInfo.attributes["commitTime"] = unicode( info.commitTime )
		pluginInfo.attributes["commitTimeReadable"] = unicode( info.commitTimeReadable )
		create_child_node( document, pluginInfo, "commitMessage", unicode( info.commitMessage ) )
		node.appendChild( pluginInfo )

		return node

	def fetchRepositoryFolder( self, remotePath ):
		'''Retrieve a remote path from the repository. The path will be retrieved with the revision specified by getRevision(). 
		The method returns the path where the folder has been stored, and a list of temporary directories to be deleted once the 
		folder is not needed anymore. The list may be empty.'''
		raise NotImplementedError()

	def describe( self, prefix, details = None, replacePatterns = True ):
		branch = 'branch {0}'.format( self.getBranch() ) if self.getBranch() else None
		tag = 'tag {0}'.format( self.getTag() ) if self.getTag() else None
		revision = 'revision {0}'.format( self.getRevision() ) if self.getRevision() else None
		elements = filter( lambda x : x, [ self.getUrl(), branch, tag, revision] )
		status = ', '.join( elements )
		self.setObjectStatus( status )
		super( SourceCodeProvider, self ).describe( prefix, details, replacePatterns )
