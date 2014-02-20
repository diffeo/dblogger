
import random
import struct
import time

from uuid import UUID

def gen_uuid(timestamp=None):
    if timestamp is None:
        timestamp = time.time()

    # 128 bit fake-uuid is 64 bits time, 64 bits random number.
    # High order bits first to keep ordering.
    bytes = struct.pack('>qLL', long(timestamp * 1024), 
                random.getrandbits(32), random.getrandbits(32))

    return UUID(bytes=bytes)

def random_slice(items):
    start = random.randint(0, len(items))
    end = random.randint(0, len(items))

def datetime_to_time(datetime):
    return time.mktime(datetime.timetuple())
