'''Query tool to retrieve :class:`dblogger.DatabaseLogHandler` results.

.. This software is released under an MIT/X11 open source license.
   Copyright 2013-2014 Diffeo, Inc.

This provides a :program:`dblogger` command-line tool.  It retrieves
messages stored in a database using
:class:`dblogger.DatabaseLogHandler`.

This supports the standard :option:`--config <yakonfig --config>`,
:option:`--dump-config <yakonfig --dump-config>`,
:option:`--verbose <dblogger --verbose>`,
:option:`--quiet <dblogger --quiet>`, and
:option:`--debug <dblogger --debug>` options.

.. program:: dblogger

.. option:: --begin <time>

Only show messages at or after `time`.  Time should be an ISO date
string of the form ``YYYY-MM-DDTHH:MM:SS.MMMMMMZ``, or any
left-truncated prefix thereof.

.. option:: --end <time>

Only show messages at or before `time`.

'''
from __future__ import absolute_import
import argparse
import logging
import re
import time

import dblogger
from dblogger.format import FixedWidthFormatter
from dblogger.logger import DatabaseLogHandler
from dblogger.utils import gen_uuid
import kvlayer
import streamcorpus
import yakonfig

class DBLoggerQuery(object):
    def __init__(self, storage_client, table_name="log"):
        self.storage = storage_client
        self.table_name = table_name
        self.last_uuid = None
        storage_client.setup_namespace({ table_name : 1 })

    def build_key_range(self, uuid_start=None, uuid_end=None):
        key_start = tuple()
        key_end = tuple()

        if uuid_start:
            key_start = (uuid_start,)

        if uuid_end:
            key_end = (uuid_end,)

        return (key_start, key_end)


    def filter(self, begin=None, end=None, filter_str=None, tail=False):
        """Get log record from the database.

        begin and end must be timestamp as returned by time.time().

        filter_str() -- An dict of filters that will match agaist log record
        fields. Not Implemented yet.

        """

        uuid_begin = uuid_end = None
        if begin:
            uuid_begin = gen_uuid(begin)
        if end:
            uuid_end = gen_uuid(end)
        key_range = self.build_key_range(uuid_begin, uuid_end)

        if filter_str:
            filter_re = re.compile(filter_str)

        while True:
            for key, rec_json in self.storage.scan(self.table_name, key_range):

                ## what is the purpose of these three lines?
                if key[0] == self.last_uuid:
                    break
                self.last_uuid = key[0]
                ##  ^^^^^ why? ^^^^^^^^

                record = DatabaseLogHandler.deserialize(rec_json)
                if filter_str and not filter_re.match(record.message):
                    continue
                yield key, record

            if not tail:
                break

            time.sleep(1)
            key_range = self.build_key_range(uuid_begin=self.last_uuid)


zulu_timestamp_re = re.compile('(?P<year>\d{4})?-?(?P<month>\d{0,2})?-?(?P<day>\d{0,2})?T?(?P<hour>\d{0,2})?:?(?P<minute>\d{0,2})?:?(?P<second>\d{0,2})?.?(?P<microsecond>\d{0,6})?Z?')
#%Y-%m-%dT%H:%M:%S.%fZ'

def complete_zulu_timestamp(partial_zulu_timestamp):
    'fill out a partial zulu_timestamp string'
    match = zulu_timestamp_re.match(partial_zulu_timestamp)
    vals = map(lambda x: x and int(x) or 0, match.groups())
    if  vals[1] == 0:
        vals[1] = 1
    if  vals[2] == 0:
        vals[2] = 1
    return '%d-%02d-%02dT%02d:%02d:%02d.%06dZ' % tuple(vals)


def main():
    parser = argparse.ArgumentParser(
        description='retrieve log messages from kvlayer')
    parser.add_argument(
        '--begin', default=None, 
        help='YYYY-MM-DDTHH:MM:SS.MMMMMMZ in UTC can be truncated at any depth')
    parser.add_argument(
        '--end', default=None, 
        help='YYYY-MM-DDTHH:MM:SS.MMMMMMZ in UTC can be truncated at any depth')
    args = yakonfig.parse_args(parser, [yakonfig, kvlayer, dblogger])

    if args.begin:
        args.begin = streamcorpus.make_stream_time(complete_zulu_timestamp(args.begin)).epoch_ticks
    if args.end:
        args.end   = streamcorpus.make_stream_time(complete_zulu_timestamp(args.end)).epoch_ticks

    client = kvlayer.client()
    query = DBLoggerQuery(client)
    formatter = FixedWidthFormatter()
    count = 0
    for key, record in query.filter(args.begin, args.end):
        print formatter.format(record)
        count += 1
    if count == 0:
        print 'no log records found'
    else:
        print 'returned %d log records' % count

if __name__ == '__main__':
    main()
