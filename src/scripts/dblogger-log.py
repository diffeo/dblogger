#!/usr/bin/env python

import argparse
import logging
import yaml

import kvlayer
from dblogger import DatabaseLogHandler


parser = argparse.ArgumentParser(description='DBLogger: cmd line logger tool.')
parser.add_argument('-c', '--config', type=file, required=True)
parser.add_argument('-l', '--level', type=int, default=logging.INFO, 
    choices=[ 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET' ])
parser.add_argument("msg")

args = parser.parse_args()

config = yaml.load(args.config)
client = kvlayer.client(config)

logger = logging.getLogger('test_logger')
logger.setLevel(logging.getLevelName(args.level))
namespace = config["namespace"]
dbhandler = DatabaseLogHandler(client, namespace)
logger.addHandler(dbhandler)

logger.log(args.level, args.msg)

