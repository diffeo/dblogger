''':mod:`logging` handler that stores log messages in a database.

.. This software is released under an MIT/X11 open source license.
   Copyright 2013-2014 Diffeo, Inc.

'''
from __future__ import absolute_import

from importlib import import_module
import time
import logging
import json
import random
import struct
import sys

from uuid import UUID

from dblogger.utils import gen_uuid
import kvlayer
import yakonfig

class DatabaseLogHandler(logging.Handler):
    '''Log handler that stores log messages in a database.

    This uses :mod:`kvlayer` to store the actual log messages.
    When the log handler is created, the caller needs to pass
    in either the :mod:`kvlayer` configuration or the actual
    :class:`kvlayer.AbstractStorage` object.  The constructor
    also accepts a virtual table name, defaulting to ``log``.

    If a global YAML file is used to configure the application, then
    YAML reference syntax can be used to share this handler's
    configuration with the global kvlayer configuration.

    .. code-block:: yaml

        kvlayer: &kvlayer
          storage_type: redis
          storage_addresses: [ 'redis.example.com:6379' ]
        logging:
          handlers:
            db:
              class: dblogger.DatabaseLogHandler
              storage_config: *kvlayer

    Log messages are stored in a table with a single UUID key, where
    the high-order bits of the UUID are in order by time.  The actual
    table values are serialized JSON representations of the log
    records.

    This log handlers adds a format string property ``%(humantime)s``
    with a time in a fixed format, and ``%(exc_text)s`` with the
    formatted traceback from an exception.  These properties are also
    included in the JSON stored in the database..

    .. automethod:: __init__

    '''
    def __init__(self, storage_client=None, table_name="log",
                 storage_config=None):
        """Create a new database log handler.

        You must either pass in ``storage_client``, an actual kvlayer
        client object, or ``storage_config``, a dictionary which will
        be passed to ``kvlayer.client()``.  Log messages
        will be stored in the table ``table_name``.

        :param storage_client: existing storage client
        :type storage_client: :class:`kvlayer.AbstractStorage`
        :param str table_name: virtual table name
        :param dict storage_config: configuration for new storage client

        """
        super(DatabaseLogHandler, self).__init__()

        if storage_client is None:
            if storage_config is None:
                raise RuntimeError('must pass either storage_client or '
                                   'storage_config')
            with yakonfig.defaulted_config(
                    [kvlayer], config=dict(kvlayer=storage_config)):
                storage_client = kvlayer.client()
            
        self.storage = storage_client
        self.table_name = table_name
        storage_client.setup_namespace({ table_name : 1 })

    def formatDBTime(self, record):
        record.humantime = time.strftime('%Y-%m-%dT%H:%M:%S-%Z', time.localtime(record.created))

    @classmethod
    def serialize(cls, record):
        xdict = dict()
        for k, v in record.__dict__.iteritems():
            if isinstance(v, tuple):
                v = list(v)
            if isinstance(v, list):
                for idx, item in enumerate(v):
                    if isinstance(item, (type, object)):
                        v[idx] = str(item)
            xdict[k] = v
        try:
            return json.dumps(xdict)
        except:
            sys.exit('failed to serialize: %r' % xdict)
            

    @classmethod
    def deserialize(cls, rec_json):
        xdict = json.loads(rec_json)
        return logging.makeLogRecord(xdict)

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
