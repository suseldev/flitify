import config
from server.flitifyserver import FlitifyServer
from storage.dbhandler import DBHandler
from apiserver.apiserver import ApiServer

import time
import logging
import threading
import os
import traceback

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



def startFlitifyServer(servConfig, rsaKey):
    logger = logging.getLogger("flitify")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("FlitifyServer: [%(asctime)s] [%(levelname)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    host = servConfig['host']
    port = servConfig['port']
    dbHandler = DBHandler()
    server = FlitifyServer(host, port, rsaKey, dbHandler)
    server_thread = threading.Thread(target=server.start, name='FlitifyServer')
    server_thread.start()
    return server

def startAPIServer(flitifyServer, apiConfig):
    logger = logging.getLogger('waitress')
    handler = logging.StreamHandler()
    formatter = logging.Formatter("APIServer: [%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    server = ApiServer(flitifyServer, host=apiConfig['host'], port=apiConfig['port'])
    server_thread = threading.Thread(target=server.start, name='ApiServer')
    server_thread.start()

def kill_on_exception(args):
    if args.thread.name not in ['FlitifyServer', 'ApiServer', 'FlitifyServer-Watchdog']:
        return
    logging.critical(f"Thread {args.thread.name} stopped, stopping server {args.exc_type.__name__}: {args.exc_value}")
    logging.critical("Traceback:\n" + "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)))
    os._exit(1)

def main():
    try:
        servConfig = config.loadServerConfig()
        apiConfig = config.loadApiConfig()
        rsaKey = open(servConfig['private_key_path'], 'rb').read()
        threading.excepthook = kill_on_exception
        flitifyServer = startFlitifyServer(servConfig, rsaKey)
        startAPIServer(flitifyServer, apiConfig)
    except Exception as e:
        logging.critical(f"Cannot launch: {e}")
        os._exit(1)

 
if __name__ == "__main__":
    main()
