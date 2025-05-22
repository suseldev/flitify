import config
from server.flitifyserver import FlitifyServer
from storage.dbhandler import DBHandler

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



def startFlitifyServer():
    servConfig = config.loadServerConfig()
    host = servConfig['host']
    port = servConfig['port']
    rsaKey = open(servConfig['private_key_path'], 'rb').read()
    dbHandler = DBHandler()
    server = FlitifyServer(host, port, rsaKey, dbHandler)
    server.start()

if __name__ == "__main__":
    startFlitifyServer()
