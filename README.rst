dblogger
========

Provides two capabilities:

1) a subclass of python logging.Handler that stores logs using kvlayer

2) command line tools for searching through logs stored in kvlayer



Format
======

Logs are stored in kvlayer using the following format:

:key: UUID generated from the created field of the LogRecord class.
:value: JSON object with the LogRecord attributes except args and msg.

For more information have a look at Python LogRecord documentation.
http://docs.python.org/2/library/logging.html#logrecord-attributes


Usage
=====

Python
------

This is a small app in Python, an example of how to use dblogger.

    import yaml
    import logging
    import kvlayer
    from dblogger import DatabaseLogHandler, DBLoggerQuery

    config = yaml.load(open("/myapp/config.yaml"))
    client = kvlayer.client(config)
    namespace = "myapp"

    logger = logging.getLogger('mymodule')
    logger.setLevel(logging.DEBUG)
    dbhandler = DatabaseLogHandler(client, namespace)
    logger.addHandler(dbhandler)

    logger.warn("this is a demo msg")



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


