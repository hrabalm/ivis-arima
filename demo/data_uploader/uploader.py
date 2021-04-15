import helpers as hp
import time
import uuid
import multiprocessing

class ProcessManager:
    def __init__(self):
        self.processes = []

    def add_process(self, function):
        self.processes.append(multiprocessing.Process(target=f))

    def add_processes(self, functions):
        for f in functions:
            self.add_process(f)

    def start(self):
        for p in self.processes:
            p.start()

    def join(self):
        for p in self.processes:
            p.join()

if __name__ == '__main__':
    time.sleep(20)
    hp.wait_for_ivis()
    hp.set_api_key(dbhost=hp.MYSQL_HOST,
                dbport=hp.MYSQL_PORT,
                dbuser=hp.MYSQL_USER,
                dbpass=hp.MYSQL_PASS,
                dbname=hp.MYSQL_DB,
                key=hp.API_KEY)

    def f():
        hp.upload_csv_wait('wait5_'+str(uuid.uuid4()), 'With Wait', 'test.csv', 1000, wait_seconds=5)

    def g():
        hp.upload_csv_wait('wait1_'+str(uuid.uuid4()), 'With Wait',
                        'test.csv', 1000, wait_seconds=1)

    pm = ProcessManager()
    pm.add_process(f)
    pm.add_process(g)

    pm.start()
    pm.join()
