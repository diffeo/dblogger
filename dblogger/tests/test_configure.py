"""tests for dblogger.configure"""

import logging
from StringIO import StringIO

import yaml

from dblogger import configure_logging

def test_default_config(capsys):
    configure_logging({})
    logger = logging.getLogger('dblogger.test_global')
    logger.critical('test')
    (out,err) = capsys.readouterr()
    print out
    # this comes from the default format string...we can't test everything,
    # but we can at least check things like
    assert err[34:46] == 'test_configu'
    assert err[52:] == 'CRITICAL test\n'

def test_change_log_level_only(capsys):
    config = """
    logging:
        version: 1
        root:
            level: DEBUG
    """
    config = yaml.load(StringIO(config))
    configure_logging(config)
    logger = logging.getLogger('dblogger.test_global')
    logger.critical('test')
    logger.debug('test 2')
    (out,err) = capsys.readouterr()
    print out
    assert err[34:46] == 'test_configu'
    assert err[52:66] == 'CRITICAL test\n'
    assert err[100:112] == 'test_configu'
    assert err[118:] == 'DEBUG    test 2\n'

def test_toplevel_config(capsys):
    config = """
    logging:
        version: 1
        formatters:
            toplevelf:
                format: 'toplevel %(levelname)s %(message)s'
        handlers:
            toplevel:
                class: logging.StreamHandler
                formatter: toplevelf
        root:
            handlers: [toplevel]
    """
    config = yaml.load(StringIO(config))
    configure_logging(config)
    logger = logging.getLogger('dblogger.test_global')
    logger.critical('test')
    (out,err) = capsys.readouterr()
    print out
    assert err == 'toplevel CRITICAL test\n'

def test_inline_config(capsys):
    config = """
    version: 1
    formatters:
        inlinef:
            format: 'inline %(levelname)s %(message)s'
    handlers:
        inline:
            class: logging.StreamHandler
            formatter: inlinef
    root:
        handlers: [inline]
    """
    config = yaml.load(StringIO(config))
    configure_logging(config)
    logger = logging.getLogger('dblogger.test_global')
    logger.critical('test')
    (out,err) = capsys.readouterr()
    print out
    assert err == 'inline CRITICAL test\n'
