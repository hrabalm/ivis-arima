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

    def h():
        hp.upload_csv_wait(f"ALO_{str(uuid.uuid4())}", "ALO Wait 10s", "data/ALO_daily.csv", 15000, wait_seconds=10)

    def i():
        hp.upload_csv_wait(f"ALO_weekly", "ALO Weekly Wait 10s", "data/ALO_weekly.csv", 1500, wait_seconds=10)

    pm = hp.ProcessManager()

    pm.add_process(h)
    pm.add_process(i)

    pm.start()
    pm.join()
