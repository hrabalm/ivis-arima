import os
import sys
import logging

# Load config from environment variables

config = {
    'MYSQL_HOST': None,
    'MYSQL_PORT': None,
    'MYSQL_DB': None,
    'MYSQL_USER': None,
    'MYSQL_PASS': None,
    'API_HOST': None,
    'API_PORT': None,
    'API_BASE': None,  # e.g. http://ivis:8082/api
    # this key will be inserted into db
    'API_KEY': '15f49b993fc23892eb07316dfedda9a10d23b491'
}


def load_config():
    failed = False
    for k in config.keys():
        if os.environ.get(k):
            config[k] = os.environ.get(k)
        elif config[k]:  # use default value if present
            pass
        else:
            failed = True
            logging.error(f'Missing required environment variable {k}')

    if failed:
        logging.critical(
            'Failed to load configuration from environment variables.')
        sys.exit(1)


load_config()
