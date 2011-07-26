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

from core.helpers.GlobalMApp import mApp
import inspect
import signal
import traceback

class MomException( Exception ):
	"""MomException encapsulates an error that occurs during a build script run."""

	def __init__( self, value, details = None ):
		Exception.__init__( self )
		self.value = value
		self.details = details
		self.__traceback = traceback.format_stack()[:-1]

		# get phase if possible
		from core.MApplication import MApplication
		if MApplication.instance:
			self.__phase = mApp().getPhase()
		else:
			self.__phase = None

		# get caller
		curframe = inspect.currentframe()
		try:
			calframe = inspect.getouterframes( curframe, 2 )
			self.__caller = calframe[1][3]
		except:
			self.__caller = '<unknown>'
		finally:
			del curframe

	def __str__( self ):
		return self.value.rstrip()

	@staticmethod
	def getReturnCode():
		raise NotImplementedError( "Abstract base class method called!" )

	def getObjectDescription( self ):
		return self.__doc__

	def getDetails( self ):
		return self.details

	def getPhase( self ):
		return self.__phase

	def getTraceback( self ):
		return self.__traceback

	def logErrorDescription( self ):
		from core.MApplication import MApplication
		phase = MApplication.Phase.getDescription( self.getPhase() )
		mApp().error( mApp(), u'error in {0} during {1} phase'.format( self.__caller, phase ) )
		mApp().error( mApp(), u'return code {0}: {1}'.format( self.getReturnCode() , unicode( self ) ) )

		if self.getDetails():
			messages = self.getDetails().splitlines()
			for message in messages:
				mApp().message( mApp(), message )

		if self.getTraceback():
			mApp().message( mApp(), "Traceback:" )
			for line in self.getTraceback():
				mApp().message( mApp(), line )


class BuildError( MomException ):
	"""A build error is raised if the build fails due to a problem caused by the project."""

	@staticmethod
	def getReturnCode():
		return 1

class ConfigurationError( MomException ):
	"""A configuration error is raised if the build fails due to a mis-configuration of the run environment.
	The error is not caused by the project, and it is not an internal error in the make-o-matic code. 
	ConfigurationErrors need to be fixed by the administrators of the CI system."""

	@staticmethod
	def getReturnCode():
		return 2

class MomError( MomException ):
	"""A MomError is raised if an error was detected that was caused by make-o-matic itself.
	MomErrors need to be fixed by the make-o-matic developers."""


	@staticmethod
	def getReturnCode():
		return 3

class AbortBuildException( MomException ):
	"""Use AbortBuildException to indicate that the build should be aborted without raising an error, 
	and without proceeding to later phases."""

	@staticmethod
	def getReturnCode():
		return 4

class InterruptedException( MomError ):
	"""This class is not used directly by MOM, it only defines the correct return code."""

	@staticmethod
	def getReturnCode():
		return signal.SIGINT + 128

def returncode_to_description( returnCode ):
	"""Returns a string representing the description of the return code"""

	if returnCode == 0: # no error
		return "Build finished successfully"
	elif returnCode == BuildError.getReturnCode():
		return "An error occurred while building the project"
	elif returnCode == ConfigurationError.getReturnCode():
		return "A configuration error occurred"
	elif returnCode == MomError.getReturnCode():
		return "An error in Make-O-Matic occurred"
	else:
		return "Something unexpected occurred"
