'''
python query handler.

Copyright 2013 Diffeo, Inc.
'''

import time
import logging
import json
import re

from dblogger.utils import gen_uuid


class DBLoggerQuery(object):
    def __init__(self, storage_client, table_name="log"):
        self.storage = storage_client
        self.table_name = table_name
        self.last_uuid = None
        storage_client.setup_namespace({ table_name : 1 })

    def build_key_range(self, uuid_start=None, uuid_end=None):
        key_start = key_end = ''

        if uuid_start:
            key_start = (uuid_start,)
            key_end = ('',)
        if uuid_end:
            key_end = (uuid_end,)

        return (key_start, key_end)


    def filter(self, start=None, end=None, filter_str=None, tail=False):
        """Get log record from the database.

        start and end must be timestamp as returned by time.time().

        filter_str() -- An dict of filters that will match agaist log record
        fields. Not Implemented yet.

        """

        uuid_start = uuid_end = None
        if start:
            uuid_start = gen_uuid(start)
        if end:
            uuid_end = gen_uuid(end)
        key_range = self.build_key_range(uuid_start, uuid_end)

        if filter_str:
            filter_re = re.compile(filter_str)

        while True:
            for uuid, value in self.storage.get(self.table_name, key_range):
                if uuid[0] == self.last_uuid:
                    break
                self.last_uuid = uuid[0]
                record = json.loads(value)
                if filter_str and not filter_re.match(record["message"]):
                    continue
                yield uuid, record

            if not tail:
                break

            time.sleep(1)
            key_range = self.build_key_range(uuid_start=self.last_uuid)
