import helpers as hp
import time
import uuid
import multiprocessing
import logging
import sys
import signal
from config import config as c

logging.basicConfig(level=logging.INFO)

def handler(signum, frame):
    sys.exit(1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    hp.wait_for_ivis()
    hp.set_api_key(dbhost=c['MYSQL_HOST'],
                   dbport=c['MYSQL_PORT'],
                   dbuser=c['MYSQL_USER'],
                   dbpass=c['MYSQL_PASSWORD'],
                   dbname=c['MYSQL_DATABASE'],
                   key=c['API_KEY'])

    def f():
        hp.upload_csv_wait('co2w5_'+str(uuid.uuid4()),
                           'CO2 Wait 5s', 'test.csv', 1000, wait_seconds=5)

    def g():
        hp.upload_csv_wait('co2w1_'+str(uuid.uuid4()), 'CO2 Wait 1s',
                           'test.csv', 1000, wait_seconds=1)

    pm = hp.ProcessManager()
    pm.add_process(f)
    pm.add_process(g)

    pm.start()
    pm.join()
