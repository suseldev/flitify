import struct
import logging

class ProtocolConnectionError(Exception):
    pass

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
        try:
            self.socket.sendall(data)
        except BrokenPipeError:
            logging.debug(f"{self.peerAddr}: connection closed during sendRaw")
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
        data = self.socket.recv(size)
        if not data:
            self.closeConnection()
            logging.debug(f"{self.peerAddr}: connection closed during recvRaw")
            raise BrokenPipeError("Connection closed by peer")
        return data

