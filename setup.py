#!/usr/bin/env python
from setuptools import setup

setup(
	name = "Make-O-Matic",
	version = "0.1.0",
	author = "KDAB",
	author_email = "make-o-matic-support@kdab.com",
	description = ( "Maker of matics" ),
	license = "GPL",
	keywords = "make-o-matic",
	url = "https://github.com/KDAB/Make-O-Matic",
	packages = [ 'mom' ],
	classifiers = [
		"Development Status :: 3 - Alpha",
		"Environment :: Console",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Programming Language :: Python",
		"Topic :: Software Development :: Build Tools",
	],
	install_requires = ['lxml'],
	entry_points = {
		"console_scripts": [
			"mom = mom.tools.mom_runner:main",
			"mom-report-converter = mom.tools.report_converter:main",
			"mom-ci = mom.tools.simple_ci:main",
			"mom-test = mom.tests.testsuite_selftest:main",
		],
	},
 )
