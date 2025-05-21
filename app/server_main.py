import config
from server.flitifyserver import FlitifyServer
from storage.dbhandler import DBHandler

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
