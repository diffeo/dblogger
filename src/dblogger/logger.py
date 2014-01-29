'''
python logging handler that stores log messages in a database

This software is released under an MIT/X11 open source license.

Copyright 2013-2014 Diffeo, Inc.
'''

from __future__ import absolute_import

from importlib import import_module
import time
import logging
import json
import random
import struct

from uuid import UUID

from dblogger.utils import gen_uuid
import kvlayer

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
    def __init__(self, storage_client=None, table_name="log",
                 storage_config=None):
        """Create a new database log handler.

        You must either pass in ``storage_client``, an actual kvlayer
        client object, or ``storage_config``, a dictionary which will
        be passed to ``kvlayer.client()``.  Log messages
        will be stored in the table ``table_name``.

        """
        super(DatabaseLogHandler, self).__init__()

        if storage_client is None:
            if storage_config is None:
                raise RuntimeError('must pass either storage_client or '
                                   'storage_config')
            storage_client = kvlayer.client(storage_config)
            
        self.storage = storage_client
        self.table_name = table_name
        storage_client.setup_namespace({ table_name : 1 })

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

        new_uuid = gen_uuid(record.created)
        dbrec = self.serialize(record)
        self.storage.put(self.table_name, ((new_uuid,), dbrec))
