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

   python -m dblogger.search -c myconfig.yaml appname namespace loglevel filter 

:filter: could be a regex to be applied to the log message or a field=regex pair,
specifying the log record field and the regex to be applied to that field.


Testing
=======

   make test

Building
========

To build the module:

    make

To create an egg package:

    make build_egg

To create RPM packages:

    make build_rpm

If you want to publish the package:

    make register

and to clean everything:

    make clean


TODO
====

- test rpm packge in a RPM platform.
- search from command line.
- 'tail -f' behavior for the log search interface.
