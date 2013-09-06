'''
python query handler.

Copyright 2013 Diffeo, Inc.
'''

import time
import logging
import json
import re

from time_uuid import TimeUUID


class DBLoggerQuery(object):
    def __init__(self, storage_client, namespace, table_name="log"):
        self.storage = storage_client
        self.namespace = namespace
        self.table_name = table_name
        storage_client.setup_namespace(namespace, { table_name : 1 })

    def filter(self, start=None, end=None, filter_str=None, tail=False):
        """Get log record from the database.
        
        start and end must be timestamp as returned by time.time().

        filter_str() -- An dict of filters that will match agaist log record
        fields. Not Implemented yet.

        """

        key_start = ''
        key_end = ''
        if start:
            uuid_start = TimeUUID.with_timestamp(start)
            key_start = (uuid_start,)
        if end:
            uuid_end = TimeUUID.with_timestamp(end)
            key_end = (uuid_end,)

        if filter_str:
            filter_re = re.compile(filter_str)

        for key, value in self.storage.get(self.table_name, (key_start, key_end)):
            record = json.loads(value)
            if filter_str and not filter_re.match(record["message"]):
                continue
            yield key, record

