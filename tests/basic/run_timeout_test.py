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

from core.Project import Project
import sys
from core.helpers.RunCommand import RunCommand

project = Project( "Simple Project Run Test", "0.5.0" )
try:
	timeout = int( sys.argv[1] )
	command = ' '.join( sys.argv[2:] )
	runner = RunCommand( project, command, timeout, True )
	runner.run()
	print( """\
RunCommand exited.

return code:
{0}

combined output:
""".format( runner.getReturnCode() ) )
	out = runner.getStdOut().decode()
	print( out )
except Exception as e:
	print( """{0} Run with timeout tester
Usage: {0} <timeout seconds> command args
Example: {0} 30 make -j4
{1}
""".format( sys.argv[0], str( e ) ) )
	sys.exit( 1 )



