
import os
import yaml
import time
import logging
import json

import pytest

import kvlayer

from dblogger import DatabaseLogHandler, DBLoggerQuery

config_path = os.path.join(os.path.dirname(__file__))

@pytest.fixture(params=[ "config_cassandra.yaml" ])
def client(request):
    config = yaml.load(open(os.path.join(config_path, request.param)))
    print config
    client = kvlayer.client(config)
    client.namespace = config["namespace"]

    def cleanup():
        client.delete_namespace(client.namespace)
    request.addfinalizer(cleanup)

    return client

def test_basic(client):
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    dbhandler = DatabaseLogHandler(client, client.namespace, "basic")
    logger.addHandler(dbhandler)

    for i in xrange(10):
        logger.warn("test %d" % i)

    query = DBLoggerQuery(client, client.namespace)
    i = 0
    for record in query.filter():
        assert record[1]["message"] == "test %d" % i
        i += 1

def test_ordering(client):
    dbhandler = DatabaseLogHandler(client, client.namespace, "ordering")
    
    for i in xrange(50):
        xdict = dict(created=time.time() + (2 ** i), message="test %d" % i)
        record = logging.makeLogRecord(xdict)
        dbhandler.emit(record)

    query = DBLoggerQuery(client, client.namespace)
    i = 0
    for record in query.filter():
        assert record[1]["message"] == "test %d" % i
        i += 1

