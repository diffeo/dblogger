
import random
import struct
import time

from uuid import UUID


def gen_uuid(timestamp=None, sequence=None):
    if timestamp is None:
        timestamp = time.time()
    if sequence is None:
        sequence = random.getrandbits(32)

    # 128 bit fake-uuid is 64 bits time, 64 bits random number.
    # High order bits first to keep ordering.
    bytes = struct.pack('>qLL', long(timestamp * 1024), sequence,
                        random.getrandbits(32))

    return UUID(bytes=bytes)


def random_slice(items):
    start = random.randint(0, len(items))
    end = random.randint(0, len(items))
    return items[start:end+1]


def datetime_to_time(datetime):
    return time.mktime(datetime.timetuple())
