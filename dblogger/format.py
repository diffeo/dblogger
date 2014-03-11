'''Formatters for :mod:`logging`.

.. This software is released under an MIT/X11 open source license.
   Copyright 2013-2014 Diffeo, Inc.

'''

import logging

class FixedWidthFormatter(logging.Formatter):
    '''Formats log messages in fixed columns.

    This adds format string properties
    ``%(fixed_width_filename_lineno)s`` containing the file name and
    line number in a 17-character-wide field, and
    ``%(fixed_width_levelname`` containing the log level padded out to
    an 8-character-wide field.

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


