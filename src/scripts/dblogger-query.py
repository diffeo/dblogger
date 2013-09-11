#!/usr/bin/env python

import argparse
import logging
import yaml
from dateutil.parser import parse

import kvlayer
from dblogger import DBLoggerQuery
from dblogger.utils import datetime_to_time


parser = argparse.ArgumentParser(description='DBLogger: cmd line logger tool.')
parser.add_argument('-c', '--config', type=file, required=True)
parser.add_argument("--start")
parser.add_argument("--end")
parser.add_argument("--filter")

args = parser.parse_args()

config = yaml.load(args.config)
client = kvlayer.client(config)
namespace = config["namespace"]

query = DBLoggerQuery(client, namespace)

query_args = {}
if args.start:
    query_args['start'] = datetime_to_time(parse(args.start))
if args.end:
    query_args['end'] = datetime_to_time(parse(args.end))
if args.filter:
    query_args['filter_str'] = args.filter

for uuid, entry in query.filter(**query_args):
    print entry['humantime'], entry['name'], entry['levelname'], entry['message']

