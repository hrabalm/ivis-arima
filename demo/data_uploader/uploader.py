#!/usr/bin/env python3

import json
import requests

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

    for signal in signals:
        data = {
            'cid': signal,
            'name': signal,
            'type': 'double',
            'settings': '{}',
            'set': cid,
            'namespace': 1,
        }

        resp = requests.post('http://localhost:8082/api/signals/' + cid, headers=headers, json=data);


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
