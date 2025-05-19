import struct
import logging

class ProtocolConnectionError(Exception):
    pass

class BaseConnection:
    def __init__(self, socket, peerAddr):
        self.socket = socket
        self.peerAddr = peerAddr
        self.peerAddr = f'{self.peerAddr[0]}:{self.peerAddr[1]}'
        self.running = True

    def closeConnection(self):
        self.running = False
        self.socket.close()

    def sendRaw(self, data: bytes):
        try:
            self.socket.sendall(data)
        except BrokenPipeError:
            logging.debug(f"{self.peerAddr}: connection closed during sendRaw")
            self.closeConnection()
            raise

    def recvRaw(self, size: int) -> bytes:
        data = self.socket.recv(size)
        if not data:
            self.closeConnection()
            logging.debug(f"{self.peerAddr}: connection closed during recvRaw")
            raise BrokenPipeError("Connection closed by peer")
        return data

