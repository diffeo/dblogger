
import os
import yaml
import time
import logging
import json
import random
import math
import uuid

import pytest

import kvlayer
from make_namespace_string import make_namespace_string

from dblogger import DatabaseLogHandler, DBLoggerQuery

config_path = os.path.join(os.path.dirname(__file__))

@pytest.fixture(params=[ "config_cassandra.yaml" ])
def client(request):
    config = yaml.load(open(os.path.join(config_path, request.param)))
    config['namespace'] = make_namespace_string()
    print config
    client = kvlayer.client(config)

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

    for i in xrange(10):
        logger.warn("test %d" % i)

    query = DBLoggerQuery(client)
    i = 0
    for record in query.filter():
        assert record[1]["message"] == "test %d" % i
        i += 1

def test_preserve_existing_tables(client):
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    dbhandler = DatabaseLogHandler(client)
    logger.addHandler(dbhandler)

    for i in xrange(10):
        logger.warn("test %d" % i)

    key = (uuid.uuid4(), uuid.uuid4())
    val = 'data'
    client.put('existing_table_1', (key, val))
    
    assert list(client.get('existing_table_1', (key, key)))[0][1] == val

def test_ordering(client):
    dbhandler = DatabaseLogHandler(client)
    
    for i in xrange(10):
        xdict = dict(created=time.time() + (2 ** i), msg="test %d" % i)
        record = logging.makeLogRecord(xdict)
        dbhandler.emit(record)

    query = DBLoggerQuery(client)
    i = 0
    for record in query.filter():
        assert record[1]["message"] == "test %d" % i
        i += 1

def test_queries(client):
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

    start = math.floor(slice[0])
    end = math.ceil(slice[-1])
    i = 0
    for record in query.filter(start=start, end=end):
        assert record[1]["message"] == "test %d" % slice[i]
        i += 1

    choice = random.choice(created_list)
    filter_str = 'test %d' % choice
    for record in query.filter(filter_str=filter_str):
        assert record[1]["message"] == "test %d" % choice

