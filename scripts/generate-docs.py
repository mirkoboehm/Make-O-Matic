#!/usr/bin/env python

from __future__ import print_function
import os, sys

def which( program ):
	def is_exe( fpath ):
		return os.path.exists( fpath ) and os.access( fpath, os.X_OK )

	fpath, fname = os.path.split( program )
	if fpath:
		if is_exe( program ):
			return program
	else:
		for path in os.environ["PATH"].split( os.pathsep ):
			exe_file = os.path.join( path, program )
			if is_exe( exe_file ):
				return exe_file

	return None

COMMAND = "doxygen"
FILE_IN = "doxygen.cfg.in"
FILE_OUT = "doxygen.cfg"

# runtime checks
if not which( COMMAND ):
	print( "Error: Doxygen missing. Exit." )
	sys.exit( 1 )

if not os.path.exists( FILE_IN ):
	print ( "Error: Run {0} from Make-O-Matic's top-level directory, where {1} is located. Exit.".format( sys.argv[0], FILE_IN ) )
	sys.exit( 1 )

# parse doxygen input files and replace placeholders
fin = open( FILE_IN )
fout = open( FILE_OUT , 'w' )

for line in fin.xreadlines():
	out = line \
			.replace( "@@(project.folders.src)", os.path.curdir )

	if not "@@" in out:
		fout.write( out )

fin.close()
fout.close()

print( "Now running doxygen, docs will be in ./html" )
os.execlp( COMMAND, COMMAND, FILE_OUT )
