import config
from config import ConfigError
from server.flitifyserver import FlitifyServer
from storage.dbhandler import DBHandler, DBFailure
from apiserver.apiserver import ApiServer

import time
import logging
import threading
import os
import traceback
import signal

shutdownEvent = threading.Event()

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.getLogger("pymongo").setLevel(logging.ERROR)

def startFlitifyServer(servConfig, rsaKey):
    """
    Initializes and starts the Flitify server in a separate daemon thread.

    Args:
        servConfig (dict): Configuration dictionary for the Flitify server, including host, port, and database settings.
        rsaKey (bytes): RSA private key used for secure communication with clients.

    Returns:
        FlitifyServer: The initialized Flitify server instance.
    """
    logger = logging.getLogger("flitify")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("FlitifyServer: [%(asctime)s] [%(levelname)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    host = servConfig['host']
    port = servConfig['port']
    dbAddress = servConfig['db_address']
    dbUser = servConfig['db_user']
    dbPassword = servConfig['db_password']
    dbName = servConfig['db_name']
    dbHandler = DBHandler(dbAddress, dbUser, dbPassword, dbName)
    server = FlitifyServer(host, port, rsaKey, dbHandler)
    server_thread = threading.Thread(target=server.start, name='FlitifyServer', daemon=True)
    server_thread.start()
    return server

def startAPIServer(flitifyServer, apiConfig):
    """
    Initializes and starts the API server in a separate daemon thread.

    Args:
        flitifyServer (FlitifyServer): Reference to the running Flitify server instance.
        apiConfig (dict): Configuration dictionary for the API server, including host, port, and API secret.
    """
    logger = logging.getLogger('waitress')
    handler = logging.StreamHandler()
    formatter = logging.Formatter("APIServer: [%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    logger = logging.getLogger('apiserver')
    handler = logging.StreamHandler()
    formatter = logging.Formatter("APIServer: [%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


    server = ApiServer(flitifyServer, host=apiConfig['host'], port=apiConfig['port'], secret=apiConfig['secret'])
    server_thread = threading.Thread(target=server.start, name='ApiServer', daemon=True)
    server_thread.start()

def graceful_shutdown(signum, frame):
    """
    Handles OS signals (SIGINT, SIGTERM) for graceful server shutdown.

    Sets a shutdown event that allows running threads to exit cleanly.
    
    Args:
        signum (int): Signal number.
        frame (frame object): Current stack frame (not used).
    """
    logging.info("[*] Shutting down servers")
    shutdownEvent.set()

def kill_on_exception(args):
    """
    Custom exception hook for critical server threads.

    If a monitored thread (FlitifyServer, ApiServer, or Watchdog) crashes,
    logs the error and immediately terminates the process.

    Args:
        args (threading.ExceptHookArgs): Exception information passed by the thread.
    """
    if args.thread.name not in ['FlitifyServer', 'ApiServer', 'FlitifyServer-Watchdog']:
        return
    logging.critical(f"Thread {args.thread.name} stopped, stopping server {args.exc_type.__name__}: {args.exc_value}")
    logging.critical("Traceback:\n" + "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)))
    os._exit(1)

def main():
    """
    Entry point for launching the Flitify Server.

    On failure, logs a critical error and exits the process.
    """
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    try:
        configPath = os.getenv("FLITIFY_CONFIG_PATH", "config_server.json")
        lConfig = config.loadServerConfig(configPath)
        servConfig = lConfig['flitify_server']
        apiConfig = lConfig['api_server']
        rsaKey = open(servConfig['private_key_path'], 'rb').read()
        threading.excepthook = kill_on_exception
        flitifyServer = startFlitifyServer(servConfig, rsaKey)
        startAPIServer(flitifyServer, apiConfig)
        shutdownEvent.wait()
    except Exception as e:
        logging.critical(f"Cannot launch: {e}")
        os._exit(1)

 
if __name__ == "__main__":
    main()
