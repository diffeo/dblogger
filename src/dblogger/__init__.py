'''
python logging handler that stores log messages in a database

Copyright 2013 Diffeo, Inc.
'''

## TODO:

# 1) organize this to use different backend databases for storage --
# cassandra and accumulo first

# 2) design simple log querying/reading requirements, and organize
# this into fields

# 3) make tests for test-driven dev
#
# - Move this to different modules.
#

import time
import logging
import json

from time_uuid import TimeUUID


class FixedWidthFormatter(logging.Formatter):
    '''
    Provides fixed-width logging display, see:
    http://stackoverflow.com/questions/6692248/python-logging-string-formatting
    '''
    filename_width = 17
    levelname_width = 8

    def format(self, record):
        max_filename_width = self.filename_width - 3 - len(str(record.lineno))
        filename = record.filename
        if len(record.filename) > max_filename_width:
            filename = record.filename[:max_filename_width]
        a = "%s:%s" % (filename, record.lineno)
        record.fixed_width_filename_lineno = a.ljust(self.filename_width)
        levelname = record.levelname
        levelname_padding = ' ' * (self.levelname_width - len(levelname))
        record.fixed_width_levelname = levelname + levelname_padding
        return super(FixedWidthFormatter, self).format(record)


class DatabaseLogHandler(logging.Handler):
    '''
    This was adapted from reading log_test14.py in the original python
    logging package that later was added to the standard library:
    http://www.red-dove.com/python_logging.html#download

    This handles log messages, which have these attrs:
    %(dbtime)s,
    %(relativeCreated)d,
    '%(name)s',
    %(levelno)d,
    '%(levelname)s',
    '%(message)s',
    '%(filename)s',
    '%(pathname)s',
    %(lineno)d,
    %(msecs)d,
    '%(exc_text)s',
    '%(thread)s'
    '''
    def __init__(self, storage_client, namespace, table_name="log"):
        logging.Handler.__init__(self)
        self.storage = storage_client
        self.namespace = namespace
        self.table_name = table_name
        storage_client.setup_namespace(namespace, { table_name : 1 })

    def formatDBTime(self, record):
        record.humantime = time.strftime('%Y-%m-%dT%H:%M:%S-%Z', time.localtime(record.created))

    def serialize(self, record):
        rec = {}
        for k, v in record.__dict__.items():
            if k in [ 'args', 'msg' ]:
                continue
            rec[str(k)] = str(v)

        return json.dumps(rec)

    def emit(self, record):
        '''
        handle a record by formatting parts of it, and pushing it into
        storage.
        '''
        self.format(record)
        self.formatDBTime(record)

        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
        else:
            record.exc_text = ''

        uuid = TimeUUID.with_timestamp(record.created)
        dbrec = self.serialize(record)
        self.storage.put(self.table_name, ((uuid,), dbrec))


class DBLoggerQuery(object):
    def __init__(self, storage_client, table_name="log"):
        self.storage = storage_client
        self.table_name = table_name


    def filter(self, time_start=None, time_end=None, filter_str={}):
        """Get log record from the database.
        
        time_start and time_end must be timestamp as returned by time.time().

        filter_str() -- An dict of filters that will match agaist log record
        fields. Not Implemented yet.

        """

        key_start = ''
        key_end = ''
        if time_start:
            uuid_start = TimeUUID.with_timestamp(time_start)
            key_start = (uuid_start,)
        if time_end:
            uuid_end = TimeUUID.with_timestamp(time_end)
            key_end = (uuid_end,)

        return self.storage.get(self.table_name, (key_start, key_end))

