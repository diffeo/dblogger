
import os
import yaml
import time
import logging
import json

import kvlayer

from dblogger import DatabaseLogHandler, DBLoggerQuery

config_path = os.path.join(os.path.dirname(__file__), 'config_cassandra.yaml')

def test_cassandra():
    config = yaml.load(open(config_path))
    client = kvlayer.client(config)
    namespace = "mytests2"

    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    dbhandler = DatabaseLogHandler(client, namespace)
    logger.addHandler(dbhandler)

    logger.warn("test")

    query = DBLoggerQuery(client)
    record = query.filter().next()
    assert record[1]["message"] == "test"

    client.delete_namespace(namespace)

