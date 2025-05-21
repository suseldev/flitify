import config
from server.flitifyserver import FlitifyServer
from storage.dbhandler import DBHandler
from crypto.utils import rsakeyutils

def startFlitifyServer():
    servConfig = config.loadServerConfig()
    host = servConfig['host']
    port = servConfig['port']
    rsaKey = rsakeyutils.loadKeyFromFile(servConfig['private_key_path'])
    dbHandler = DBHandler()
    server = FlitifyServer(host, port, rsaKey, dbHandler)
    server.start()

if __name__ == "__main__":
    startFlitifyServer()
