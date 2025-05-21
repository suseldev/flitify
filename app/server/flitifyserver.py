import threading
import socket
import logging

from server.handlers.clienthandler import ClientHandler
from network.protocolconnection import ServerProtocolConnection


class ClientThread(threading.Thread):
    def __init__(self, socket, peerAddr, rsaKey, dbHandler):
        self.socket = socket
        self.peerAddr = peerAddr
        self.rsaKey = rsaKey
        self.dbHandler = dbHandler
        super().__init__()

    def run(self):
        logging.debug(f'{self.peerAddr[0]}:{self.peerAddr[1]}: starting thread')
        self.connection = ServerProtocolConnection(self.socket, self.peerAddr, self.rsaKey, self.dbHandler)
        self.client = ClientHandler(self.connection)
        self.client.ping()
        print(f'Status: {self.client.getStatus()}')

class FlitifyServer:
    def __init__(self, host, port, rsaKey, dbHandler):
        self.host = host
        self.port = port
        self.dbHandler = dbHandler
        self.rsaKey = rsaKey
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.running = True
        logging.info(f'FlitifyServer listening on {self.host}:{self.port}')

        try:
            while self.running:
                client_sock, client_addr = self.sock.accept()
                logging.info(f'{client_addr[0]}:{client_addr[1]}: connection accepted')
                try:
                    self.clientThread = ClientThread(client_sock, client_addr, self.rsaKey, self.dbHandler)
                    self.clientThread.start()
                except Exception as e:
                    logging.error(f'{client_addr[0]}:{client_addr[1]}: uncaught exception while running ClientThread: {e}')
        except KeyboardInterrupt:
            logging.info('Shutting down server, keyboard interrupt detected')


