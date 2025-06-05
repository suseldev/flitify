import threading
import socket
import logging
import time

from server.handlers.clienthandler import ClientHandler
from network.protocolconnection import ServerProtocolConnection

import constants

class ClientThread(threading.Thread):
    """
    Represents a dedicated thread handling a single client connection.
    Responsible for initializing the secure protocol connection and the client handler.
    """
    def __init__(self, socket, peerAddr, rsaKey, dbHandler):
        """
        Initializes the client thread.

        Args:
            socket (socket.socket): The socket object for communication.
            peerAddr (tuple): IP address and port of the connecting client.
            rsaKey: Server RSA private key used for secure communication.
            dbHandler: Database handler for retrieving authentication secrets.
        """
        self.socket = socket
        self.peerAddr = peerAddr
        self.rsaKey = rsaKey
        self.client = None
        self.dbHandler = dbHandler
        self.logger = logging.getLogger('flitify')
        super().__init__()

    def getClient(self):
        """
        Returns the initialized client handler.

        Returns:
            ClientHandler or None: The associated client handler, if initialized.
        """
        return self.client

    def run(self):
        """
        Starts the thread.
        """
        self.logger.debug(f'{self.peerAddr[0]}:{self.peerAddr[1]}: Starting thread')
        self.connection = ServerProtocolConnection(self.socket, self.peerAddr, self.rsaKey, self.dbHandler)
        self.client = ClientHandler(self.connection)

class FlitifyServer:
    def __init__(self, host, port, rsaKey, dbHandler):
        """
        Initializes the server with specified configuration and starts the watchdog thread.

        Args:
            host (str): The host IP or hostname to bind the server socket to.
            port (int): Port number to listen on.
            rsaKey: RSA private key used to establish secure communication.
            dbHandler: Database handler for client authentication data.
        """
        self.host = host
        self.port = port
        self.dbHandler = dbHandler
        self.rsaKey = rsaKey
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.waitingClients = []
        self.watchdogThread = threading.Thread(target=self._clientsWatchdog, daemon=True, name='FlitifyServer-Watchdog')
        self.watchdogThread.start()
        self.activeClients = {}
        self.logger = logging.getLogger('flitify')
    
    def getClientList(self) -> list:
        """
        Retrieves a list of currently active client IDs.

        Returns:
            list: A list of active client identifiers.
        """
        clientList = [] 
        for client in self.activeClients.keys():
            clientList.append(client)
        return clientList
        
    def getClientById(self, clientId:str) -> ClientHandler | None:
        """
        Retrieves a client handler by its unique identifier.

        Args:
            clientId (str): The identifier of the client.

        Returns:
            ClientHandler or None: The associated client handler, or None if not found.
        """
        if clientId not in self.activeClients:
            return None
        return self.activeClients[clientId]

    def start(self):
        """
        Starts the server.
        """
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.running = True
        self.logger.info(f'FlitifyServer listening on {self.host}:{self.port}')

        while self.running:
            client_sock, client_addr = self.sock.accept()
            self.logger.info(f'{client_addr[0]}:{client_addr[1]}: Connection accepted')
            client_sock.settimeout(constants.SOCKET_TIMEOUT)
            try:
                self.waitingClients.append(ClientThread(client_sock, client_addr, self.rsaKey, self.dbHandler))
                self.waitingClients[-1].start()
            except Exception as e:
                self.logger.error(f'{client_addr[0]}:{client_addr[1]}: Uncaught exception while running ClientThread: {e}')

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
                            self.logger.warning(f'{connection.peerAddr} ({connection.clientId}): duplicate detected, closing connection')
                            connection.closeConnectionWithReason('You are a duplicate!')
                        else:
                            self.logger.debug(f'Watchdog: adding {client.getClient().getConnection().peerAddr} ({connection.clientId}) to activeClients')
                            self.activeClients[connection.clientId] = client
                        
                        if client in self.waitingClients:
                            self.logger.debug(f'Watchdog: removing {client.getClient().getConnection().peerAddr} from waitingClients')
                            self.waitingClients.remove(client)
                            continue

                    if not connection.running and client in self.waitingClients:
                        self.logger.debug(f'Watchdog: removing {client.getClient().getConnection().peerAddr} from waitingClients')
                        self.waitingClients.remove(client)

                for client_id in list(self.activeClients.keys()):
                    client = self.activeClients[client_id]
                    if not client.getClient().getConnection().running:
                        self.logger.debug(f'Watchdog: client {client.getClient().getConnection().peerAddr} ({client_id}) offline, removing from active clients')
                        del self.activeClients[client_id]
            except Exception as e:
                self.logger.critical(f'Watchdog: uncaught exception: {e}')
                raise
