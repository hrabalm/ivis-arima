#!/usr/bin/env python3

import json
import csv
import requests
import pendulum

# this key will be inserted into db
API_KEY = '15f49b993fc23892eb07316dfedda9a10d23b491'

headers = {
    'access-token': API_KEY
}

x = {
    'ts': 'datetime',
    'arbitrary_float_1': 0,
    'arbitrary_float_2': 0,
}


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
        'http://localhost:8082/api/signal-sets', headers=headers, json=data)

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

        resp = requests.post('http://localhost:8082/api/signals/' + cid, headers=headers, json=data);
        print(resp.json())

def upload_record(setCid, record):
    setId = 4
    data = {

    }
    resp = requests.post('http://localhost:8082/api/signal-set-records/' + str(setId), headers=headers, json=record)
    print(record)

def process_csv_file(filename):
    ts_field = 'ts'
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file, delimiter=',')

        for i, value in enumerate(reader):
            ts = value[ts_field]
            ts = pendulum.parse(ts)
            print('ts:', ts)
            signals = {k: v for k, v in value.items() if k != ts_field}
            print('signals:', signals)
            ts = ts.to_date_string()

            if i == 0:
                name = filename.split('.')[0]
                create_signal_set(name, name, [k for k in signals])
                upload_record(name, {'id': ts, 'ts': ts, **signals})
            else:
                upload_record(name, {'id': ts, 'ts': ts, **signals})



def main():
    resp = requests.get(
        'http://localhost:8082/api/predictions/0', headers=headers)
    print(resp.text)

    resp = requests.post(
        'http://localhost:8082/api/signal-set/0', headers=headers, data={})
    print(resp.text)


if __name__ == '__main__':
    set_api_key(dbhost='localhost',
                dbport=9991,
                dbuser='ivis',
                dbpass='Chahw7aev9re',
                dbname='ivis',
                key=API_KEY)
    main()
    #create_signal_set('testSignalSet', 'Test Signal Set', ['ahoj'])
    process_csv_file('test.csv')
