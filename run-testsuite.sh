#!/bin/sh

PYTHONPATH_BAK=$PYTHONPATH

PYTHONPATH=$PWD:$PYTHONPATH

echo "*** Starting tests (PYTHONPATH: $PYTHONPATH) ***"
cd tests && python testsuite.py

PYTHONPATH=$PYTHONPATH_BAK
