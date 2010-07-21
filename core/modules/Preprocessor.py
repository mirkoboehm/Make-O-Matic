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
from core.Plugin import Plugin
from core.executomat.Action import Action
from core.helpers.TypeCheckers import check_for_nonempty_string_or_none

class _PreprocessorAction( Action ):
	'''The _PreprocessorAction performs the input file conversion.'''

	def __init__( self, preprocessor, name = None ):
		Action.__init__( self, name )

	def setPreprocessor( self, preprocessor ):
		assert isinstance( preprocessor, Preprocessor )
		self.__preprocessor = preprocessor

	def _getPreprocessor( self ):
		return self.__preprocessor

class Preprocessor( Plugin ):
	'''Preprocessor takes a textual input file, applies variables from various dictionaries, and produces an output file.
	The preprocessor generates an action that performs the conversion of the input file, and adds it as a post action to a step. 
	By default, the action is added to the project-checkout step. It can be changed by setting the step property of the 
	preprocessor.'''

	def __init__( self, name = None, inputFilename = None, outputFilename = None, step = 'project-checkout' ):
		Plugin.__init__( self, name )
		self.setInputFilename( inputFilename )
		self.setOutputFilename( outputFilename )
		self.setStep( step )

	def setInputFilename( self, name ):
		check_for_nonempty_string_or_none( name, 'The input filename must be a non-empty string, or None.' )
		self.__inputFilename = name

	def getInputFilename( self ):
		return self.__inputFilename

	def setOutputFilename( self, name ):
		check_for_nonempty_string_or_none( name, 'The output filename must be a non-empty string, or None.' )
		self.__outputFilename = name

	def getOutputFilename( self ):
		return self.__outputFilename

	def setStep( self, step ):
		check_for_nonempty_string_or_none( step, 'The step must be a non-empty string that is a step name, or None.' )
		self.__step = step

	def getStep( self ):
		return self.__step

	def setup( self, project ):
		step = project.getExecutomat().getStep( self.getStep() )
		action = _PreprocessorAction( self )
		step.addPostAction( action )
