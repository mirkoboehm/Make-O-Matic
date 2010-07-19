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
from core.Defaults import Defaults
import os
from core.Exceptions import ConfigurationError
from core.executomat.Step import Step

class Settings( Defaults ):
	"""Settings stores all configurable values for a build script run."""

	def __init__( self ):
		'''Constructor'''
		# this applies the defaults:
		Defaults.__init__( self )

	def initialize( self, project ):
		'''Determine the script run settings. 
		In the constructor, defaults will be applied. 
		First, configuration files will be parsed.
		Second, command line arguments will be applied. 
		Third, commit message commands will be applied. This can be disabled by a parameter (step three).
		On error, a subclass of MomException is thrown.
		Logging and reporting is not available at this stage yet.'''
		# first, parse configuration files:
		self.evalConfigurationFiles( project )
		# second, apply parameters:
		# the option parser will exit the script if any of the options are not valid
		project.getParameters().parse()
		project.getParameters().apply( self )
		# third, apply commit message commands:
		# FIXME

	def calculateBuildSequence( self, project ):
		buildType = self.get( Settings.ProjectBuildType, True ).lower()
		assert len( buildType ) == 1
		allBuildSteps = self.get( Settings.ProjectBuildSteps, True )
		buildSteps = []
		for buildStep in allBuildSteps:
			# FIXME maybe this could be a unit test?
			assert len( buildStep ) == 2
			name, types = buildStep
			assert types.lower() == types
			stepName = Step( name )
			stepName.setEnabled( buildType in types )
			buildSteps.append( stepName )
		project.debug( self, 'build type: {0} ({1})'.format( buildType.upper(), self.getBuildTypeDescription( buildType ) ) )
		# apply customizations passed as command line parameters:
		switches = project.getParameters().getBuildSteps()
		if switches:
			project.debugN( self, 3, 'build sequence before command line parameters: {0}'
						.format( self.__getBuildSequenceDescription( buildSteps ) ) )
			customSteps = switches.split( ',' )
			for switch in customSteps:
				stepName = None
				enable = None
				if switch.startswith( 'enable-' ):
					stepName = switch[ len( 'enable-' ) : ].strip()
					enable = True
				elif switch.startswith( 'disable-' ):
					stepName = switch[ len( 'disable-' ) : ].strip()
					enable = False
				else:
					raise ConfigurationError( 'Build sequence switch "{0}" does not start with enable- or disable-!'
											.format( switch ) )
				# apply:
				found = False
				for step in buildSteps:
					if step.getName() == stepName:
						step.setEnabled( enable )
						found = True
				if not found:
					raise ConfigurationError( 'Undefined build step "{0}" in command line arguments!'.format( stepName ) )
		project.debug( self, 'build sequence: {0}'.format( self.__getBuildSequenceDescription( buildSteps ) ) )
		return buildSteps

	def __getBuildSequenceDescription( self, buildSteps ):
		# debug info:
		texts = []
		for stepName in buildSteps:
			texts.append( '{0} ({1})'.format( stepName.getName(), 'enabled' if stepName.getEnabled() else 'disabled' ) )
		return ', '.join( texts )

	def evalConfigurationFiles( self, project ):
		filename = 'config.py'
		globalConfigFile = os.path.join( '/', 'etc', 'mom', filename )
		homeDir = os.environ['HOME']
		localConfigFile = os.path.join( homeDir, '.mom', filename )
		configFiles = [ globalConfigFile, localConfigFile]
		for configFile in configFiles:
			if not os.path.isfile( configFile ):
				project.debugN( self, 3, 'Configuration file "{0}" does not exist, continuing.'.format( configFile ) )
				continue
			project.debugN( self, 2, 'Loading configuration file "{0}"'.format( configFile ) )
			try:
				globals = { 'project' : project }
				with open( configFile ) as f:
					code = f.read()
					exec( code, globals )
				project.debug( self, 'Configuration file "{0}" loaded successfully'.format( configFile ) )
			except SyntaxError as e:
				raise ConfigurationError( 'The configuration file "{0}" contains a syntax error: "{1}"'.format( configFile, str( e ) ) )
			except Exception as e: # we need to catch all exceptions, since we are calling user code 
				raise ConfigurationError( 'The configuration file "{0}" contains an error: "{1}"'.format( configFile, str( e ) ) )
			except: # we need to catch all exceptions, since we are calling user code 
				raise ConfigurationError( 'The configuration file "{0}" contains an unknown error!'.format( configFile ) )

	def getBuildTypeDescription( self, type ):
		descriptions = self.get( Settings.ProjectBuildTypeDescriptions )
		if type in descriptions:
			return descriptions[type]
		else:
			return None
