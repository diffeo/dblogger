'''
python logging handler that stores log messages in a database

Copyright 2013 Diffeo, Inc.
'''

## TODO:

# 1) organize this to use different backend databases for storage --
# cassandra and accumulo first

# 2) design simple log querying/reading requirements, and organize
# this into fields

# 3) make tests for test-driven dev

import sys
import time
import logging
import traceback

class FixedWidthFormatter(logging.Formatter):
    '''
    Provides fixed-width logging display, see:
    http://stackoverflow.com/questions/6692248/python-logging-string-formatting
    '''
    filename_width = 17
    levelname_width = 8

    def format(self, record):
        max_filename_width = self.filename_width - 3 - len(str(record.lineno))
        filename = record.filename
        if len(record.filename) > max_filename_width:
            filename = record.filename[:max_filename_width]
        a = "%s:%s" % (filename, record.lineno)
        record.fixed_width_filename_lineno = a.ljust(self.filename_width)
        levelname = record.levelname
        levelname_padding = ' ' * (self.levelname_width - len(levelname))
        record.fixed_width_levelname = levelname + levelname_padding
        return super(FixedWidthFormatter, self).format(record)

class DatabaseLogHandler(logging.Handler):
    '''
    This was adapted from reading log_test14.py in the original python
    logging package that later was added to the standard library:
    http://www.red-dove.com/python_logging.html#download

    This handles log messages, which have these attrs:
    %(dbtime)s,
    %(relativeCreated)d,
    '%(name)s',
    %(levelno)d,
    '%(levelname)s',
    '%(message)s',
    '%(filename)s',
    '%(pathname)s',
    %(lineno)d,
    %(msecs)d,
    '%(exc_text)s',
    '%(thread)s'
    '''
    def __init__(self, storage_client):
        logging.Handler.__init__(self)
        self.storage = storage_client

    def formatDBTime(self, record):
        record.dbtime = time.strftime('%Y-%m-%dT%H:%M:%S-%Z', time.localtime(record.created))

    def emit(self, record):
        '''
        handle a record by formatting parts of it, and pushing it into
        storage
        '''
        ## use default formatting
        self.format(record)
        ## now set the database time up
        self.formatDBTime(record)
        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
        else:
            record.exc_text = ''

        ## pass the record as a dictionary to the storage client.log()
        rec = {}
        for k, v in record.__dict__.items():
            rec[str(k)] = str(v)
        try:
            self.storage.log(rec)
        except Exception, exc: #self.storage.StorageClosed:
            ## gracelessly do nothing
            pass

        ## if some part of those steps fail, we want the exception to
        ## bubble all the way up, so we do not do this:
        #except:
        #    ei = sys.exc_info()
        #    traceback.print_exception(ei[0], ei[1], ei[2], None, sys.stderr)
        #    del ei

    #def flush... is missing

    def close(self):
        self.storage.close()
        ## flush first?
        logging.Handler.close(self)
