#!/usr/bin/env python3

import json
import csv
import time
import requests
import pendulum
import uuid
import multiprocessing
import os

# this key will be inserted into db
API_KEY = '15f49b993fc23892eb07316dfedda9a10d23b491'
API_BASE = 'http://localhost:8082/api'
MYSQL_HOST = 'localhost'
MYSQL_PORT = 9991

if os.environ.get('DB_HOST'):
    MYSQL_HOST = os.environ.get('DB_HOST')
if os.environ.get('DB_PORT'):
    MYSQL_PORT = os.environ.get('DB_PORT')
if os.environ.get('API_BASE'):
    API_BASE = os.environ.get('API_BASE')

headers = {
    'access-token': API_KEY
}

DATE_FORMAT = "YYYY-MM-DD[T]HH:mm:ss.SSS[Z]"  # brackets are used for escaping

def upload_csv():
    pass

def set_api_key(dbhost, dbport, dbuser, dbpass, dbname, key):
    """Directly set the access_token to key in the database

    Args:
        key ([type]): [description]
    """
    from mysql.connector import connect, Error
    query = f'''UPDATE users
                SET access_token = "{key}"
                WHERE id = 1'''
    try:
        with connect(
            host=dbhost,
            port=dbport,
            user=dbuser,
            database=dbname,
            password=dbpass,
        ) as connection:
            print(connection)
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def create_signal_set(cid, name, signals=[]):
    data = {
        'cid': cid,
        'type': 'normal',
        'name': name,
        'kind': 'time_series',
        'namespace': 1,
    }
    resp = requests.post(
        API_BASE + '/signal-sets', headers=headers, json=data)
    setId = resp.json()

    # create signals other than 'ts', which is added automatically because
    # kind = 'time_series'
    for signal in signals:
        data = {
            'cid': signal,
            'name': signal,
            'type': 'double',
            'settings': '{}',
            'set': cid,
            'namespace': 1,
            'source': 'raw',
            'weight_list': 0,  # make signals visible in client
        }

        resp = requests.post(API_BASE + '/signals/' + cid, headers=headers, json=data);
        # signalId = resp.json()

    return setId

def upload_record(setId, record):
    resp = requests.post(API_BASE + '/signal-set-records/' + str(setId), headers=headers, json=record)
    print("record text:", resp.text)

def shift_csv_file(filename, output, shift='y', ts_field='ts'):
    # firstly, find first and last timestamp
    first_ts = None
    last_ts = None
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            if not first_ts:
                first_ts = row[ts_field]
            last_ts = row[ts_field]

    first_ts = pendulum.parse(first_ts)
    last_ts = pendulum.parse(last_ts)

    # find proper shift
    shifts = {
        'd': pendulum.Duration(days=1),
        'y': pendulum.duration(years=1)
    }

    mul = 0
    delta = shifts[shift]
    now = pendulum.now()

    while first_ts + (mul * delta) < now and first_ts + ((mul + 1) * delta) < now:
        mul += 1

    # while (now - (first_ts+(mul+1)*delta))

    delta *= mul

    with open(filename, mode='r') as file, open(output, mode='w') as outfile:
        reader = csv.DictReader(file, delimiter=',')
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames, dialect='excel')

        writer.writeheader()
        previous_ts = None
        for row in reader:
            ts = pendulum.parse(row[ts_field])+delta
            row[ts_field] = ts.format(DATE_FORMAT)
            if previous_ts != ts:
                writer.writerow(row)
            else:
                pass  # throw away duplciatate timestamps (e.g. february 28 for years)
            previous_ts = ts

def wait_for_ts(ts):
    import time
    now = pendulum.now()
    if ts > now:
        print("Waiting", (ts-now).in_seconds(), "seconds.")
        time.sleep((ts-now).in_seconds())

def process_csv_file(set_cid, set_name, filename):
    ts_field = 'ts'

    with open(filename, mode='r') as file:
        reader = csv.DictReader(file, delimiter=',')

        for i, value in enumerate(reader):
            ts = pendulum.parse(value[ts_field])
            signals = {k: v for k, v in value.items() if k != ts_field}
            ts_str = ts.format(DATE_FORMAT)

            if i == 0:
                setId = create_signal_set(set_cid, set_name, [k for k in signals])
                upload_record(setId, {'id': ts_str, 'signals': {'ts': ts_str, **signals}})
            else:
                wait_for_ts(ts)
                upload_record(setId, {'id': ts_str, 'signals': {'ts': ts_str, **signals}})


def upload_csv2(set_cid: str, set_name: str, filename: str, ts_field='ts'):
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file, delimiter=',')

        for i, row in enumerate(reader):
            ts = pendulum.parse(row[ts_field])
            ts_str = ts.format(DATE_FORMAT)
            signals = {k: v for k, v in row.items() if k != ts_field}
            signals_with_ts = {'ts': ts_str, **signals}

            if i == 0:
                setId = create_signal_set(
                    set_cid, set_name, [k for k in signals])

            wait_for_ts(ts)

            record = {'id': ts_str, 'signals': signals_with_ts}
            upload_record(setId, record)


def upload_csv_shifted(set_cid: str, set_name: str, filename: str, ts_field='ts', shift='y'):
    shifted_name = filename + str(uuid.uuid4()) + '.shifted'
    shift_csv_file(filename, shifted_name, shift=shift, ts_field=ts_field)
    upload_csv2(set_cid, set_name, shifted_name, ts_field)

def upload_csv_wait(set_cid: str, set_name: str, filename: str, batch_size, ts_field='ts', wait_seconds=10):
    """Upload first `batch_size` rows in a batch and then add records one by
    one with specified wait time.

    Args:
        set_cid (str): [description] Signal set cid
        set_name (str): [description] Signal set name
        filename (str): [description] Source csv file
        batch_size ([type]): [description]
        ts_field (str, optional): [description]. Defaults to 'ts'.
        wait_seconds (int, optional): [description]. Defaults to 10.
    """
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file, delimiter=',')

        for i, row in enumerate(reader):
            ts = pendulum.parse(row[ts_field])
            ts_str = ts.format(DATE_FORMAT)
            signals = {k: v for k, v in row.items() if k != ts_field}
            signals_with_ts = {'ts': ts_str, **signals}

            if i == 0:
                setId = create_signal_set(set_cid, set_name, [k for k in signals])

            if i >= batch_size:
                time.sleep(wait_seconds)

            record = {'id': ts_str, 'signals': signals_with_ts}
            upload_record(setId, record)

def main():
    resp = requests.get(
        API_BASE + '/predictions/0', headers=headers)
    print(resp.text)

    resp = requests.post(
        API_BASE + '/signal-set/0', headers=headers, data={})
    print(resp.text)

    # Usage:
    # upload(filename, setCid, setName, shift=year)


if __name__ == '__main__':
    time.sleep(20)
    set_api_key(dbhost=MYSQL_HOST,
                dbport=MYSQL_PORT,
                dbuser='ivis',
                dbpass='Chahw7aev9re',
                dbname='ivis',
                key=API_KEY)
    main()

    def f():
        upload_csv_wait('wait5_'+str(uuid.uuid4()), 'With Wait', 'test.csv', 1000, wait_seconds=5)

    def g():
        upload_csv_wait('wait1_'+str(uuid.uuid4()), 'With Wait',
                        'test.csv', 1000, wait_seconds=1)

    p1 = multiprocessing.Process(target=f)
    p2 = multiprocessing.Process(target=g)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
