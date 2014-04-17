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
by the :mod:`logging.config` module.  The default configuration
includes a formatter named ``fixed`` and a handler named ``console``
bound to the root logger, and a further console handler named
``debug`` not bound anywhere.

Command-line options
====================

.. program:: dblogger

All programs that use :mod:`dblogger` support shared command-line
options.  If not changed in the configuration, the defaults write
:data:`logging.INFO` level output to the console, and
:option:`--verbose` enables all debug-level logging.

.. option:: --verbose, -v

Include more output, increasing the ``console`` log handler's level
one step.  This can be included multiple times.  If the program is
more verbose than quiet and the ``console`` log handler is not
attached to the root logger, adds it.

.. option:: --quiet, -q

Include less output, decreasing the ``console`` log handler's level
one step.  This can be included multiple times.

.. option:: --debug <logger>

Write debug-level output for `logger` to the ``debug`` log handler.
This can be included multiple times.

Recipes
=======

To enable debug-level logging everywhere in an application using this
package alongside a YAML-based configuration system, include a
top-level block in the YAML file:

.. code-block:: yaml

    logging:
      root:
        level: DEBUG

To enable debug-level logging for a specific package in the
configuration file:

.. code-block:: yaml

    logging:
      loggers:
        some.other.package:
          level: DEBUG

To write debug logs globally to a file:

.. code-block:: yaml

    logging:
        file:
          class: logging.FileHandler
          filename: /tmp/dblogger.log
          formatter: fixed
      root:
        handlers: [console, file]

For further details about what is allowed, see the Python library
:mod:`logging.config` documentation.

Logging tools
=============

.. autoclass:: DatabaseLogHandler
   :show-inheritance:

.. autoclass:: FixedWidthFormatter
   :show-inheritance:

Initial logging setup
=====================

Include :mod:`dblogger` in your :func:`yakonfig.parse_args` call
to do all of the initial setup.  When control returns to your
application, logging will be fully set up.

Older programs that do not yet support this interface use:

.. autofunction:: configure_logging

:program:`dblogger` query tool
==============================

.. automodule:: dblogger.query

'''
from __future__ import absolute_import
from dblogger.configure import config_name, default_config, add_arguments, \
    runtime_keys, normalize_config
from dblogger.configure import configure_logging
from dblogger.format import FixedWidthFormatter
from dblogger.logger import DatabaseLogHandler
from dblogger.query import *
