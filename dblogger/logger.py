''':mod:`logging` handler that stores log messages in a database.

.. This software is released under an MIT/X11 open source license.
   Copyright 2013-2014 Diffeo, Inc.

'''
from __future__ import absolute_import

from importlib import import_module
import time
import logging
import json
import cPickle as pickle
import random
import struct
import sys
import traceback

from uuid import UUID
from tblib import pickling_support
pickling_support.install()  ## register traceback smarts with pickle

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
    def deserialize(cls, rec_pickle):
        try:
            xdict = pickle.loads(rec_pickle)

        except Exception, exc:
            xdict = {'msg': 'warning!!!! failed to unpickle: %r' % rec_pickle}

        return logging.makeLogRecord(xdict)


    def emit(self, record):
        '''
        handle a record by formatting parts of it, and pushing it into
        storage.
        '''
        self.format(record)
        self.formatDBTime(record)

        failure = []
        if record.args:
            try:
                ## cannot serialize arbitrary args, because they might not be
                ## picklable, so do the string now
                record.msg = record.msg % record.args
                record.args = None
            except Exception, exc:
                failure.append('failed to run string formatting on provided args')
                failure.append(traceback.format_exc(exc))
                failure.append('record.msg = %r' % record.msg)
                failure.append('record.args = %r' % (record.args,))
                failure.append('logging failed so shutting down entire process')

        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
        else:
            record.exc_text = ''

        new_uuid = gen_uuid(record.created)

        try:
            dbrec = pickle.dumps(record.__dict__,  protocol=pickle.HIGHEST_PROTOCOL)
        except Exception, exc:
            failure.append('failed to dump log record, will shutdown')
            failure.append(traceback.format_exc(exc))
            failure.append('failed to pickle the __dict__ on: record=%r' % record)
            failure.append('failed to pickle: record.__dict__=%r' % record.__dict__)
            failure.append('logging failed so shutting down entire process')

        if failure:
            dbrec = '\n'.join(failure)

        ## send it to the DB... especially if it is a failure
        self.storage.put(self.table_name, ((new_uuid,), dbrec))

        if failure:
            ## shutdown the process when logging fails
            sys.exit(dbrec)
