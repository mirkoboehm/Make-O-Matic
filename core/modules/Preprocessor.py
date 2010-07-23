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
import os
from core.Plugin import Plugin
from core.executomat.Action import Action
from core.helpers.TypeCheckers import check_for_path_or_none, check_for_string, check_for_nonempty_string_or_none
import re
from core.Exceptions import BuildError

class _PreprocessorAction( Action ):
	'''The _PreprocessorAction performs the input file conversion.'''

	def __init__( self, preprocessor, name = None ):
		Action.__init__( self, name )
		self.setPreprocessor( preprocessor )
		# set up a regular expression that searches for the place holders:
		self.__regex = re.compile( r'{(@@\(.*\))}*' )

	def setPreprocessor( self, preprocessor ):
		assert preprocessor == None or isinstance( preprocessor, Preprocessor )
		self.__preprocessor = preprocessor

	def _getPreprocessor( self ):
		return self.__preprocessor

	def getRegex( self ):
		return self.__regex

	def getLogDescription( self ):
		return '"{0}" -> "{1}"'.format( 
					self._getPreprocessor().getInputFilename().getFilename(),
					self._getPreprocessor().getOutputFilename().getFilename() )

	def run( self, project ):
		try:
			self.__project = project
			project.debugN( self, 3, 'Creating "{0}" from "{1}"'.format( 
					self._getPreprocessor().getOutputFilename(),
					self._getPreprocessor().getInputFilename() ) )
			self._process()
			project.debugN( self, 2, 'Successfully created "{0}" from "{1}"'.format( 
					self._getPreprocessor().getOutputFilename(),
					self._getPreprocessor().getInputFilename() ) )
		finally:
			self.__project = None

	def _process( self ):
		# open input file for reading
		inputPath = os.path.join( str( self._getPreprocessor().getInputFilename() ) )
		if not os.path.isfile( inputPath ):
			raise BuildError( 'Input file "{0}" does not exist.'.format( inputPath ) )
		with open( inputPath ) as input:
			with open( str( self._getPreprocessor().getOutputFilename() ), 'w' ) as output:
				# read line by line, replace contents, write line by line
				while True:
					line = input.readline()
					if not line: break
					result = self.processLine( line )
					output.write( result )

	def processLine( self, line ):
		'''Process a line of text, and return the result.'''
		check_for_string( line, 'processLine only accepts string input.' )
		if not line:
			return ''
		result = ''
		text = line[:]
		while text:
			result, text = self.__processToken( result, text )
		return result

	def __processToken( self, result, text ):
		index = text.find( '@@(' )
		if index == -1:
			# no place holder was found, append all text to the result, return text empty
			result += text
			return result, ''
		# a place holder was found at index
		# ... copy text before the place holder into result
		result += text[:index]
		text = text[index:]
		# now the token begins at zero, find closing bracket
		pos = 3
		level = 1
		while level > 0:
			if pos == len( text ):
				raise BuildError( 'Unbalanced place holders in "{0}"'.format( text ) )
			if text[pos] == ')':
				level -= 1
			elif text[pos] == '(':
				level += 1
			else:
				pass
			pos += 1
		pattern = text[:pos]
		replacement = self.replace( pattern )
		result += replacement
		text = text[pos:]
		return result, text

	def replace( self, pattern ):
		assert pattern.startswith( '@@(' ) and pattern.endswith( ')' )
		code = pattern[3:-1]
		if code == '@@':
			return '@@'
		elif code == '':
			return ''
		pieces = code.split( '.' )
		if pieces[0] == 'project':
			if len( pieces ) < 2:
				return '[MOM PP: not understood: {0}'.format( code )
			if pieces[1] == 'settings':
				if len( pieces ) < 3:
					return '[MOM PP: missing setting name: {0}'.format( code )
				setting = '.'.join( pieces[2:] )
				return self._getSettingText( setting )
			if pieces[1] == 'folders':
				if len( pieces ) < 3:
					return '[MOM PP: missing folder name: {0}'.format( code )
				folder = '.'.join( pieces[2:] )
				return self._getFolderName( folder )
			return '[MOM PP: unknown place holder: {0}'.format( code )
		return '[MOM PP: unknown: {0}]'.format( code )

	def _getSettingText( self, setting ):
		if not self.__project:
			return '[MOM PP: project not initialized]'
		value = self.__project.getSettings().get( setting, False )
		if not value:
			self.__project.debugN( self, 2, 'Undefined setting "{0}"'.format( setting ) )
			return ''
		return str( value )

	def _getFolderName( self, folder ):
		if not self.__project:
			return '[MOM PP: project not initialized]'
		if folder == 'src':
			return self.__project.getFolderManager().getSourceDir()
		elif folder == 'tmp':
			return self.__project.getFolderManager().getTempDir()
		elif folder == 'docs':
			return self.__project.getFolderManager().getDocsDir()
		elif folder == 'packages':
			return self.__project.getFolderManager().getPackagesDir()
		else:
			self.__project.debugN( self, 2, 'Unknown folder id "{0}"'.format( folder ) )
			return ''

class Preprocessor( Plugin ):
	'''Preprocessor takes a textual input file, applies variables from various dictionaries, and produces an output file.
	The preprocessor generates an action that performs the conversion of the input file, and adds it as a post action to a step. 
	By default, the action is added to the project-checkout step. It can be changed by setting the step property of the 
	preprocessor.
	The preprocessor searches place holders in the format of @@(variable-name) in the input file, and replaces them with the 
	content provided by the internal dictionary. A place holder in the form of @@(@@) resolves to @@.'''

	def __init__( self, name = None, inputFilename = None, outputFilename = None, step = 'project-checkout' ):
		Plugin.__init__( self, name )
		self.setInputFilename( inputFilename )
		self.setOutputFilename( outputFilename )
		self.setStep( step )

	def setInputFilename( self, name ):
		check_for_path_or_none( name, 'The input filename must be a non-empty string, or None.' )
		self.__inputFilename = name

	def getInputFilename( self ):
		return self.__inputFilename

	def setOutputFilename( self, name ):
		check_for_path_or_none( name, 'The output filename must be a non-empty string, or None.' )
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
