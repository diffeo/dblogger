"""Globally configure logging from a dictionary.

.. This software is released under an MIT/X11 open source license.
   Copyright 2014 Diffeo Inc.

Purpose
=======

Call :func:`dblogger.configure_logging`` with a configuration
dictionary, such as the global configuration given to :mod:`yakonfig`.
This will perform the logging configuration described there, and set
reasonable defaults if there is no configuration.

If the dictionary passed to :func:`configure_logging` contains a key
``logging``, that key's value is used as the logging configuration;
otherwise if the dictionary looks like logging configuration itself,
it is used directly; otherwise only default settings are used.

Module Contents
===============

"""

from __future__ import absolute_import

import logging.config

# yakonfig configuration metadata
config_name = 'logging'
default_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'verbose': 0,
    'quiet': 0,
    'debug': [],
    'formatters': {
        'fixed': {
            '()': 'dblogger.FixedWidthFormatter',
            'format': ('%(asctime)-23s pid=%(process)-5d '
                       '%(fixed_width_filename_lineno)s '
                       '%(fixed_width_levelname)s %(message)s'),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'fixed',
            'level': 'INFO',
        },
        'debug': {
            'class': 'logging.StreamHandler',
            'formatter': 'fixed',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'NOTSET',
    },
    'loggers': {
    },
}
def add_arguments(parser):
    parser.add_argument('--verbose', '-v', action='count',
                        help='produce more output')
    parser.add_argument('--quiet', '-q', action='count',
                        help='produce less output')
    parser.add_argument('--debug', action='append', metavar='LOGGER',
                        help='enable debug logging for specific modules')
runtime_keys = {
    'verbose': 'verbose',
    'quiet': 'quiet',
    'debug': 'debug',
}
def normalize_config(config):
    # Adjust console logging level
    verbosity = config.get('verbose', 0) - config.get('quiet', 0)
    if 'handlers' in config:
        if 'console' in config['handlers']:
            level = config['handlers']['console'].get('level', logging.INFO)
            if not isinstance(level, int):
                level = logging.getLevelName(level)
            level -= verbosity * 10
            # adjust to be in bounds
            level = min(level, logging.CRITICAL)
            level = max(level, logging.NOTSET)
            # bring back to a string
            try:
                level = logging.getLevelName(level)
            except KeyError, e:
                pass
            # stash
            config['handlers']['console']['level'] = level

    # Re-bind console logger if required
    if verbosity > 0:
        config.setdefault('root', {})
        config['root'].setdefault('handlers', [])
        if 'console' not in config['root']['handlers']:
            config['root']['handlers'].append('console')

    # Enable debug logging
    config.setdefault('loggers', {})
    for logger in config.get('debug', []):
        config['loggers'].setdefault(logger, {})
        config['loggers'][logger].setdefault('handlers', [])
        config['loggers'][logger]['handlers'].append('debug')

    # We've used these options and integrated them into other things,
    # so reset them
    for option in ('verbose', 'quiet', 'debug'):
        config[option] = default_config[option]

    # Fire everything off
    logging.config.dictConfig(config)

def configure_logging(config):
    """One-time global logging configuration.

    Set up logging as described in ``config``.  ``config`` should be a
    top-level configuration dictionary with a key ``logging``, and the
    value of that key is used as a configuration dictionary for
    :mod:`logging.config`.  If there is no ``logging`` key but there
    is a ``version: 1`` key/value, ``config`` is used directly as the
    configuration.  Otherwise a minimal default configuration is used.

    If the configuration does not define any handlers, then a default
    console log handler will be created and bound to the root logger.
    This will use a formatter named ``fixed``, defining it if
    necessary.

    :param dict config: :mod:`logging.config` setup dictionary

    .. deprecated:: 0.4.0
        Pass :mod:`dblogger` to :func:`yakonfig.parse_args` instead.

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
                           '%(fixed_width_levelname)s %(message)s'),
            }
        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'formatter': 'fixed',
        }
        config.setdefault('root', {})
        config['root']['handlers'] = ['console']
    
    # also, we must set this magic flag, or any logger created at the
    # module level will stop working
    config['disable_existing_loggers'] = False

    logging.config.dictConfig(config)
