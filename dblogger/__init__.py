'''Python logging setup and database backend.

.. This software is released under an MIT/X11 open source license.
   Copyright 2013-2014 Diffeo, Inc.

This package provides basic support tools for the standard Python
:mod:`logging` package.  In particular, it exposes the
:mod:`logging.config` setup language through configuration layers
such as :mod:`yakonfig`, and it includes some basic database
support utilities.

Applications that use this support a ``logging`` block in their
configuration files.  This may have any valid logging setup supported
by the :mod:`logging.config` module.  If no handlers are defined in
the configuration, the initial setup will create a formatter named
``fixed`` and a handler named ``console`` and bind these to the root
logger.

Recipes
=======

To enable debug-level logging everywhere in an application using this
package alongside a YAML-based configuration system, include a
top-level block in the YAML file:

.. code-block:: yaml

    logging:
      root:
        level: DEBUG

To enable info-level logging to the console everywhere, but also
debug-level logging for a specific package:

.. code-block:: yaml

    logging:
      root:
        level: INFO
      loggers:
        some.other.package:
          level: DEBUG

To have info-level logging to the console and also debug-level logging
to a file, you need to recreate the default logger setup.

.. code-block:: yaml

    logging:
      formatters:
        fixed:
          '()': dblogger.FixedWidthFormatter
          format: '%(asctime)-23s pid=%(process)-5d %(fixed_width_filename_lineno)s %(fixed_width_levelname)s %(message)s'
      handlers:
        console:
          class: logging.StreamHandler
          formatter: fixed
          level: INFO
        file:
          class: logging.FileHandler
          filename: /tmp/dblogger.log
          formatter: fixed
      root:
        level: DEBUG
        handlers: [console, file]

Logging tools
=============

.. autoclass:: DatabaseLogHandler
   :show-inheritance:

.. autoclass:: FixedWidthFormatter
   :show-inheritance:

Initial logging setup
=====================

.. autofunction:: configure_logging

Database log query tool
=======================

.. automodule:: dblogger.query

'''
from __future__ import absolute_import
from dblogger.configure import configure_logging
from dblogger.format import FixedWidthFormatter
from dblogger.logger import DatabaseLogHandler
from dblogger.query import *
