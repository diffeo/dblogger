"""Globally configure logging from a dictionary.

Purpose
=======

Call ``dblogger.configure_logging()`` with a configuration dictionary,
such as the global configuration given to yakonfig.  This will perform
the logging configuration described there, and set reasonable defaults
if there is no configuration.

If the dictionary passed to ``configure_logging()`` contains a key
``logging``, that key's value is used as the logging configuration;
otherwise if the dictionary looks like logging configuration itself,
it is used directly; otherwise only default settings are used.  For
the actual configuration schema, see the Python documentation at
http://docs.python.org/2.7/library/logging.config.html#configuration-dictionary-schema


Implementation Details
======================


This software is released under an MIT/X11 open source license.

Copyright 2014 Diffeo Inc.

"""

from __future__ import absolute_import

import logging.config

def configure_logging(config):
    """One-time global logging configuration.

    Set up logging as described in ``config``.  ``config`` should be a
    top-level configuration dictionary with a key ``logging``, and the
    value of that key is used as a configuration dictionary for
    ``logging.config``.  If there is no ``logging`` key but there is a
    ``version: 1`` key/value, ``config`` is used directly as the
    configuration.  Otherwise a minimal default configuration is used.

    If the configuration does not define any handlers, then a default
    console log handler will be created and bound to the root logger.
    This will use a formatter named ``fixed``, defining it if necessary.

    """
    # find the actual logging config dictionary
    if 'logging' in config:
        config = config['logging']
        config.setdefault('version', 1)
    elif config.get('version') == 1:
        config = config
    else:
        config = { 'version': 1 }

    # create default handler if required
    if len(config.setdefault('handlers', {})) == 0:
        config.setdefault('formatters', {})
        if 'fixed' not in config['formatters']:
            config['formatters']['fixed'] = {
                '()': 'dblogger.FixedWidthFormatter',
                'format': ('%(asctime)-23s pid=%(process)-5d '
                           '%(fixed_width_filename_lineno)s '
                           '%(fixed_width_levelname)s %(message)s')
            }
        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'formatter': 'fixed'
        }
        config.setdefault('root', {})
        config['root']['handlers'] = ['console']
    
    # also, we must set this magic flag, or any logger created at the
    # module level will stop working
    config['disable_existing_loggers'] = False

    logging.config.dictConfig(config)
