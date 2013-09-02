'''
python query handler.

Copyright 2013 Diffeo, Inc.
'''

import time
import logging
import json

from time_uuid import TimeUUID


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

        for key, value in self.storage.get(self.table_name, (key_start, key_end)):
            yield key, json.loads(value)

