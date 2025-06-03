import os
import logging
import threading
import signal

from storage.backenddbhandler import DBHandler
from api.flitifywebbackend import FlitifyWebBackend
import config


shutdownEvent = threading.Event()

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.getLogger("pymongo").setLevel(logging.ERROR)

def startBackendApiServer(backendConfig):
    logger = logging.getLogger('waitress')
    handler = logging.StreamHandler()
    formatter = logging.Formatter("BackendAPIServer: [%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    logger = logging.getLogger('backendapiserver')
    handler = logging.StreamHandler()
    formatter = logging.Formatter("BackendAPIServer: [%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    dbAddress = backendConfig['db_address']
    dbUser = backendConfig['db_user']
    dbPassword = backendConfig['db_password']
    dbName = backendConfig['db_name']

    dbHandler = DBHandler(dbAddress, dbUser, dbPassword, dbName)
    
    # Init user 
    if os.getenv("FLITIFY_INIT_USERNAME", None) and os.getenv("FLITIFY_INIT_PASSWORD", None):
        logging.info(f"Creating init user from env variables")
        dbHandler.createUser(os.getenv("FLITIFY_INIT_USERNAME"), os.getenv("FLITIFY_INIT_PASSWORD"))

    server = FlitifyWebBackend(dbHandler, backendConfig['jwt_secret'], backendConfig['jwt_expiration_seconds'], internal_api_host=backendConfig['internal_api_host'], internal_api_secret=backendConfig['internal_api_secret'], host=backendConfig['host'], port=backendConfig['port'])
    server_thread = threading.Thread(target=server.start, name='BackendApiServer', daemon=True)
    server_thread.start()

def kill_on_exception(args):
    if args.thread.name in ['BackendApiServer']:
        return
    logging.critical(f"Thread {args.thread.name} stopped, stopping backend server {args.exc_type.__name__}: {args.exc_value}")

def graceful_shutdown(signum, frame):
    logging.info("Shutting down server")
    shutdownEvent.set()

def main():
    try:
        signal.signal(signal.SIGINT, graceful_shutdown)
        signal.signal(signal.SIGTERM, graceful_shutdown)
        configPath = os.getenv("FLITIFY_BACKEND_CONFIG_PATH", "config_backend.json")
        backendConfig = config.loadBackendConfig(configPath)
        startBackendApiServer(backendConfig)
        shutdownEvent.wait()
    except Exception as e:
        logging.critical(f"Cannot launch FlitifyWebBackend: {e}")
        raise
        os._exit(1)

if __name__ == "__main__":
    main()


