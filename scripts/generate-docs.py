#!/usr/bin/env python

import os, sys

COMMAND = "doxygen"
FILE_IN = "doxygen.cfg.in"
FILE_OUT = "doxygen.cfg"

fin = open( FILE_IN )
fout = open( FILE_OUT , 'w' )

for line in fin.xreadlines():
	out = line \
			.replace( "@@(project.folders.src)", os.path.curdir )

	if not "@@" in out:
		fout.write( out )

fin.close()
fout.close()

print "Now running doxygen, docs will be in ./html"
os.execlp( COMMAND, COMMAND, FILE_OUT )
