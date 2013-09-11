
import random
import struct

from uuid import UUID

def gen_uuid(timestamp=None):
    if timestamp is None:
        timestamp = time.time()

    # 128 bit fake-uuid is 64 bits time, 64 bits random number.
    # High order bits first to keep ordering.
    bytes = struct.pack('>qLL', long(timestamp * 1024), 
                random.getrandbits(32), random.getrandbits(32))

    return UUID(bytes=bytes)

