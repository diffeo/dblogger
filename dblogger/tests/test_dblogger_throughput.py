

import time
import pytest
import kvlayer
import logging
import multiprocessing

import yakonfig

from dblogger.tests.test_dblogger import client ## fixture that cleans up

from dblogger import DatabaseLogHandler, DBLoggerQuery


ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s pid=%(process)d %(filename)s:%(lineno)d %(levelname)s: %(message)s')
ch.setLevel('DEBUG')
ch.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(ch)

def worker(config, num_records):
    yakonfig.set_global_config(dict(kvlayer=config))
    client = kvlayer.client()
    dbhandler = DatabaseLogHandler(client)
    logger = logging.getLogger('foo')
    logger.addHandler(dbhandler)
    for i in xrange(num_records):
        logger.critical('a message: %d', i)
    logger.critical('finished')

def cleanup(results):
    for res in results:
        try:
            res.get(0)
        except multiprocessing.TimeoutError:
            continue
        except Exception, exc:
            logger.critical('trapped child exception', exc_info=True)
            raise
        else:
            ## if it gets here, slot should always be finished
            assert res.ready()
            results.remove(res)

    return len(results)

@pytest.mark.performance
def test_queries_throughput(client):
    num_tasks = 10
    num_records = 100
    num_children = 10
    pool = multiprocessing.Pool(num_children, maxtasksperchild=1)
    results = []
    for x in xrange(num_tasks):
        results.append(
            pool.apply_async(worker, args=(client._config, num_records)))

    query = DBLoggerQuery(client)

    timeout = 60
    start_time = time.time()
    while time.time() - start_time < timeout:
        if cleanup(results) == 0:
            logger.critical('finished')
            break

    elapsed = time.time() - start_time
    expected_count = num_records * num_tasks + num_tasks
    logger.critical('finished logging %d messages in %.1f sec --> %.1f per sec',
                    expected_count, elapsed, float(expected_count) / elapsed)

    count = 0
    for key, record in query.filter():
        logger.critical( record )
        assert record.message
        count += 1
    
    assert count == expected_count
