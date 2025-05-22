import struct
import logging

import constants

class BaseConnection:
    """
    Basic connection wrapper for socket communication.

    Args:
        socket (socket): socket object
        peerAddr ((<str>, int)): address of the peer
    """
    def __init__(self, socket, peerAddr):
        self.socket = socket
        self.peerAddr = peerAddr
        self.peerAddr = f'{self.peerAddr[0]}:{self.peerAddr[1]}'
        self.running = True

    def closeConnection(self):
        """
        Closes the socket and marks the connection as not running.
        """
        self.running = False
        self.socket.close()

    def sendRaw(self, data: bytes):
        """
        Sends raw data over the socket.

        Args:
            data (bytes): data to be sent

        Raises:
            BrokenPipeError: if the connection is closed during sending
        """
        if not self.running:
            raise BrokenPipeError("Attempted to send on a closed connection")
        try:
            self.socket.sendall(data)
        except BrokenPipeError:
            logging.debug(f"{self.peerAddr}: Connection closed during sendRaw")
            self.closeConnection()
            raise

    def recvRaw(self, size: int) -> bytes:
        """
        Receive raw message from the socket.

        Args:
            size (int): Maximum number of bytes received

        Returns:
            bytes: Received data

        Raises:
            BrokenPipeError: If the connection is closed by the peer
        """
        if not self.running:
            raise BrokenPipeError("Attempted to recv on a closed connection")
        data = self.socket.recv(size)
        if not data:
            self.closeConnection()
            logging.debug(f"{self.peerAddr}: Connection closed during recvRaw")
            raise BrokenPipeError("Connection closed")
        return data

    def recvLarge(self) -> bytes:
        """
        Receives a large block of data that was sent using sendLarge.

        Returns:
            bytes: the received raw data
        """
        size_bytes = self.recvRaw(4)
        size = int.from_bytes(size_bytes, 'big')
        data = b''
        while len(data) < size:
            data += self.recvRaw(constants.MESSAGE_SIZE)
        return data

    def sendLarge(self, data:bytes):
        """
        Sends a large block of data.

        Args:
            data (bytes): data to be send
        """
        size = len(data).to_bytes(4, 'big')
        self.sendRaw(size)
        self.sendRaw(data)

