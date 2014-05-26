from __future__ import absolute_import
import os
import yaml
import time
import logging
import random
import math
import uuid
import subprocess
import pytest
import sys

import kvlayer
import yakonfig

from dblogger import DatabaseLogHandler, DBLoggerQuery
from dblogger.query import complete_zulu_timestamp

config_path = os.path.join(os.path.dirname(__file__))

@pytest.fixture(scope='function')
def client(request, namespace_string, redis_address):
    config = dict(
        namespace = namespace_string,
        storage_type = 'redis',
        app_name = 'dbltest',
        storage_addresses = [redis_address],
        )
    print config
    yakonfig.set_global_config(dict(kvlayer=config))
    client = kvlayer.client()

    client.setup_namespace(
        dict(existing_table_1=2,
             existing_table_2=2))

    def cleanup():
        client.delete_namespace()
    request.addfinalizer(cleanup)

    return client

def test_basic(client):
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    dbhandler = DatabaseLogHandler(client)
    logger.addHandler(dbhandler)
    try:
        for i in xrange(10):
            logger.warn("test %d" % i)

        query = DBLoggerQuery(client)
        i = 0
        for key, record in query.filter():
            assert record.message == "test %d" % i
            i += 1
    finally:
        logger.removeHandler(dbhandler)

def test_log_exception_info(client):
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    dbhandler = DatabaseLogHandler(client)
    logger.addHandler(dbhandler)
    try:
        try:
            raise Exception('hello!')
        except:
            logger.warn("test with exception", exc_info=True)

        query = DBLoggerQuery(client)
        for key, record in query.filter():
            assert record.message
    finally:
        logger.removeHandler(dbhandler)

def test_configuration(client):
    """create the logger from the configuration, not the client object"""
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    dbhandler = DatabaseLogHandler(storage_config=client._config)
    logger.addHandler(dbhandler)
    try:
        messages = ['test {0}'.format(i) for i in xrange(10)]
        for m in messages: logger.warn(m)

        query = DBLoggerQuery(client)
        responses = [record.message for key, record in query.filter()]
        assert responses == messages
    finally:
        logger.removeHandler(dbhandler)

def test_preserve_existing_tables(client):
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    dbhandler = DatabaseLogHandler(client)
    logger.addHandler(dbhandler)

    try:
        for i in xrange(10):
            logger.warn("test %d" % i)

        key = (uuid.uuid4(), uuid.uuid4())
        val = 'data'
        client.put('existing_table_1', (key, val))
    
        assert list(client.get('existing_table_1', key))[0][1] == val
    finally:
        logger.removeHandler(dbhandler)

def test_ordering(client):
    dbhandler = DatabaseLogHandler(client)

    for i in xrange(10):
        xdict = dict(created=time.time() + (2 ** i), msg="test %d" % i)
        record = logging.makeLogRecord(xdict)
        dbhandler.emit(record)

    query = DBLoggerQuery(client)
    i = 0
    for key, record in query.filter():
        assert record.message == "test %d" % i
        i += 1

def test_queries_simple(client):
    dbhandler = DatabaseLogHandler(client)

    created_list = []
    for i in xrange(2, 10):
        created = time.time() + (2 ** i)
        created_list.append(created)
        xdict = dict(created=created, msg="test %d" % created)
        record = logging.makeLogRecord(xdict)
        dbhandler.emit(record)

    query = DBLoggerQuery(client)

    i = random.randint(0, len(created_list)-2)
    j = random.randint(i+2, len(created_list))
    slice = created_list[i:j]

    begin = math.floor(slice[0])
    end = math.ceil(slice[-1])
    i = 0
    for key, record in query.filter(begin=begin, end=end):
        assert record.message == "test %d" % slice[i]
        i += 1

    choice = random.choice(created_list)
    filter_str = 'test %d' % choice
    for key, record in query.filter(filter_str=filter_str):
        assert record.message == "test %d" % choice

def test_queries_simple2(client):
    dbhandler = DatabaseLogHandler(client)

    now = time.time()
    created_list = [now + 2 ** i for i in xrange(2,10)]
    messages = ['test {0}'.format(c) for c in created_list]
    for (created,msg) in zip(created_list, messages):
        xdict = dict(created=created, msg=msg)
        record = logging.makeLogRecord(xdict)
        dbhandler.emit(record)

    query = DBLoggerQuery(client)

    i = random.randint(0, len(created_list)-2)
    queries = created_list[i:]  ## no end
    expected = messages[i:]

    begin = math.floor(queries[0])
    end = None  ## no end
    response = query.filter(begin=begin, end=end)
    responses = [record.message for key, record in response]
    assert responses == expected

    (choice,expected) = random.choice(zip(created_list, messages))
    response = query.filter(filter_str=expected)
    responses = [record.message for key, record in response]
    assert responses == [expected]

def test_queries_cli(client):
    dbhandler = DatabaseLogHandler(client)

    created_list = []
    for i in xrange(2, 10):
        created = time.time() + (2 ** i)
        created_list.append(created)
        xdict = dict(created=created, msg="test %d" % created)
        record = logging.makeLogRecord(xdict)
        dbhandler.emit(record)

    child = subprocess.Popen(
        [sys.executable, '-m', 'dblogger.query',
         '--app-name', 'dbltest',
         '--namespace', client._config['namespace'],
         '--storage-type', client._config['storage_type'],
         '--storage-address', client._config['storage_addresses'][0],
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    child.wait()

    out = child.stdout.read()
    err = child.stderr.read()

    assert child.returncode == 0
    assert out

def test_complete_zulu_timestamp():
    assert complete_zulu_timestamp('1998-10') == '1998-10-01T00:00:00.000000Z'

def test_queries_cli2(client):
    dbhandler = DatabaseLogHandler(client)

    created_list = []
    for i in xrange(2, 10):
        created = time.time() + (2 ** i)
        created_list.append(created)
        xdict = dict(created=created, msg="test %d" % created)
        record = logging.makeLogRecord(xdict)
        dbhandler.emit(record)

    child = subprocess.Popen(
        [sys.executable, '-m', 'dblogger.query',
         '--app-name', 'dbltest',
         '--namespace', client._config['namespace'],
         '--storage-type', client._config['storage_type'],
         '--storage-address', client._config['storage_addresses'][0],
         '--begin', '1998-01-03T08',
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    child.wait()

    out = child.stdout.read()
    err = child.stderr.read()

    assert child.returncode == 0, err
    assert out
