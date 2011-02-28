#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Make-O-Matic.
# 
# Copyright (C) 2010 Klaralvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike McQuaid <mike.mcquaid@kdab.com>
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

from core.helpers.BoilerPlate import BuildConfiguration
from core.plugins.builders.generators.QMakeBuilder import QMakeBuilder
from core.plugins.packagers.CPack import CPack

build, config = BuildConfiguration( 'Jom', 'git://gitorious.org/qt-labs/jom.git', '1.0.0' )

config.addPlugin( QMakeBuilder() )
config.addPlugin( CPack( sourcePackage = True ) )

build.build()
