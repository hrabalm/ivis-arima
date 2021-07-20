import logging
import signal
import sys

import pendulum

import helpers as hp
from config import config as c

logging.basicConfig(level=logging.INFO)


def handler(signum, frame):
    sys.exit(1)


def now():
    """Returns current int timestamp"""
    return pendulum.now().int_timestamp


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    hp.wait_for_ivis()
    hp.set_api_key(dbhost=c['MYSQL_HOST'],
                   dbport=c['MYSQL_PORT'],
                   dbuser=c['MYSQL_USER'],
                   dbpass=c['MYSQL_PASSWORD'],
                   dbname=c['MYSQL_DATABASE'],
                   key=c['API_KEY'])

    def g():
        hp.upload_csv_wait(f"ALO_filtered_{now()}",
                           "ALO Filtered Wait 10s",
                           "data/ALO_filtered.csv", 15000, wait_seconds=10)

    def h():
        hp.upload_csv_wait(f"ALO_daily_{now()}",
                           "ALO Daily Wait 10s",
                           "data/ALO_daily.csv", 15000, wait_seconds=10)

    def i():
        hp.upload_csv_wait(f"ALO_weekly_{now()}",
                           "ALO Weekly Wait 10s",
                           "data/ALO_weekly.csv", 1500, wait_seconds=10)

    pm = hp.ProcessManager()

    pm.add_process(g)
    pm.add_process(h)
    pm.add_process(i)

    pm.start()
    pm.join()
