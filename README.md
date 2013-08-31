dblogger
========

Provides two capabilities:

1) a subclass of python logging.Handler that stores logs using kvlayer

2) command line tools for searching through logs stored in kvlayer



Format
======

Logs are stored in kvlayer using the following format:

.... Diego, please expand this




Usage
=====
Python
------

.... Diego, please write out example code snippets for using this in a python app



Command Line
------------

.... Diego, please invent appropriate command line interfaces and
scripts for this.  For exmample, something like for a first version:


   python -m dblogger.search -c myconfig.yaml  appname  namespace   loglevel  filterword  | less



Testing
=======

.... Diego, please invent a test application for exercising kvlayer
and make it both a test that we can run via `make test` and also an
illustration of how to use this.  The test should use subprocess to
call the CLI

If you put the tests into src/tests/dblogger/.... then pytest will run
them


Building
========

The Makefile contains targets for ... Diego, please take a look at the
Makefile and let's discuss.  Our autobuild system will run whatever is
in `make test`


