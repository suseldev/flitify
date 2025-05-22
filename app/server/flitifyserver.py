import threading
import socket
import logging
import time

from server.handlers.clienthandler import ClientHandler
from network.protocolconnection import ServerProtocolConnection

import constants

class ClientThread(threading.Thread):
    def __init__(self, socket, peerAddr, rsaKey, dbHandler):
        self.socket = socket
        self.peerAddr = peerAddr
        self.rsaKey = rsaKey
        self.client = None
        self.dbHandler = dbHandler
        super().__init__()

    def getClient(self):
         return self.client

    def run(self):
        logging.debug(f'{self.peerAddr[0]}:{self.peerAddr[1]}: Starting thread')
        self.connection = ServerProtocolConnection(self.socket, self.peerAddr, self.rsaKey, self.dbHandler)
        self.client = ClientHandler(self.connection)
        self.client.ping()

class FlitifyServer:
    def __init__(self, host, port, rsaKey, dbHandler):
        self.host = host
        self.port = port
        self.dbHandler = dbHandler
        self.rsaKey = rsaKey
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.waitingClients = []
        self.watchdogThread = threading.Thread(target=self._clientsWatchdog, daemon=True)
        self.watchdogThread.start()
        self.activeClients = {}
    
    def getClientById(self, clientId:str) -> ClientHandler:
        pass

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.running = True
        logging.info(f'FlitifyServer listening on {self.host}:{self.port}')

        try:
            while self.running:
                client_sock, client_addr = self.sock.accept()
                logging.info(f'{client_addr[0]}:{client_addr[1]}: Connection accepted')
                try:
                    self.waitingClients.append(ClientThread(client_sock, client_addr, self.rsaKey, self.dbHandler))
                    self.waitingClients[-1].start()
                except Exception as e:
                    logging.error(f'{client_addr[0]}:{client_addr[1]}: Uncaught exception while running ClientThread: {e}')
        except KeyboardInterrupt:
            logging.info('Shutting down server, keyboard interrupt detected')

    def _clientsWatchdog(self, interval=constants.INTERVAL):
        while True:
            try:
                time.sleep(interval)
                for client in list(self.waitingClients):
                    if not client.getClient():
                        self.waitingClients.remove(client)
                        continue
                    connection = client.getClient().getConnection()
                    if connection.clientId:
                        if connection.clientId in self.activeClients:
                            logging.warning(f'{connection.peerAddr} ({connection.clientId}): duplicate detected, closing connection')
                            connection.closeConnectionWithReason('You are a duplicate!')
                        else:
                            logging.debug(f'Watchdog: adding {client.getClient().getConnection().peerAddr} ({connection.clientId}) to activeClients')
                            self.activeClients[connection.clientId] = client
                        
                        if client in self.waitingClients:
                            logging.debug(f'Watchdog: removing {client.getClient().getConnection().peerAddr} from waitingClients')
                            self.waitingClients.remove(client)
                            continue

                    if not connection.running and client in self.waitingClients:
                        logging.debug(f'Watchdog: removing {client.getClient().getConnection().peerAddr} from waitingClients')
                        self.waitingClients.remove(client)

                for client_id in list(self.activeClients.keys()):
                    client = self.activeClients[client_id]
                    if not client.getClient().getConnection().running:
                        logging.debug(f'Watchdog: client {client.getClient().getConnection().peerAddr} ({client_id}) offline, removing from active clients')
                        del self.activeClients[client_id]
                logging.debug(f'Watchdog: waiting clients: {len(self.waitingClients)}, active clients: {len(self.activeClients)}')
            except Exception as e:
                logging.critical(f'Watchdog: uncaught exception: {e}')
                raise
