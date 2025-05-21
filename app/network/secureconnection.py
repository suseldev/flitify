import logging

from network.baseconnection import BaseConnection
from crypto import cryptohelper

import socket

import constants

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



class ProtocolVersionError(Exception):
    pass

class SecureConnection(BaseConnection):
    """
    Base class representing a secure connection using AES encryption with RSA key exchange.

    Args:
        socket (socket): socket object for the connection
        peerAddr ((str, int)): address of the peer (host, port)
        rsaKey (bytes): exported server's RSA key
    """

    def __init__(self, socket, peerAddr, rsaKey):
        super().__init__(socket, peerAddr)
        self.rsa = cryptohelper.CryptoHelperRSA(rsaKey)
        self.aes = None
        self._performKeyExchange()

    def _performKeyExchange(self):
        """ Performs AES key exchange using RSA encryption. """
        raise NotImplementedError()

    def sendEncrypted(self, data: bytes):
        """
        Encrypts the given data using AES and sends it through the socket.

        Args:
            data (bytes): the plaintext data to encrypt and send
        """
        data = self.aes.encrypt(data)
        self.sendRaw(data)

    def recvEncrypted(self, size: int) -> bytes:
        """
        Receives encrypted data of the specified size, decrypts it using AES, and returns the plaintext

        Args:
            size (int): the number of bytes to receive

        Returns:
            bytes: the decrypted plaintext data
        """
        data = self.recvRaw(size)
        data = self.aes.decrypt(data)
        return data

    def sendEncryptedLarge(self, data:bytes): 
        """
        Sends a large payload of arbitrary length using AES encryption
        Args:
            data (bytes): the plaintext data to encrypt and send
        """
        data = self.aes.encrypt(data)
        self.sendLarge(data)

    def recvEncryptedLarge(self) -> bytes:
        """
        Receives a large encrypted payload using AES decryption.
        
        Returns:
            bytes: the decrypted plaintext data
        """
        data = self.recvLarge()
        data = self.aes.decrypt(data)
        return data

class ServerSecureConnection(SecureConnection):
    """
    Secure connection implementation for the server side.

    Args:
        socket (socket): socket object for the connection
        peerAddr ((str, int)): address of the peer (host, port)
        rsaKey (bytes): the server's private RSA key for decrypting the AES key
    """

    def __init__(self, socket, peerAddr, rsaKey):
        super().__init__(socket, peerAddr, rsaKey)

    def _performKeyExchange(self):
        """ Refer to base class documentation. """
        try:
            protocolMsg = 'FLITIFY_V' + constants.PROTOCOL_VERSION
            self.sendRaw(protocolMsg.encode())
            logging.debug(f'{self.peerAddr}: Greeting sent: {protocolMsg}')
            encMsg = self.recvRaw(constants.MESSAGE_SIZE)
            aesKey = self.rsa.decrypt(encMsg)
            self.aes = cryptohelper.CryptoHelperAES(aesKey)
            logging.debug(f"{self.peerAddr}: AES key recieved")
            self.sendEncrypted(b'HNDSHK_PING')
            testMsg = self.recvEncrypted(constants.MESSAGE_SIZE)
            if testMsg != b'HNDSHK_PONG':
                raise ValueError(f'Incorrect handshake message: {testMsg}')
            logging.info(f"{self.peerAddr}: Handshake finished")
        except ValueError as e:
            logging.warning(f"{self.peerAddr}: Unexpected data format during key exchange, closing connection: {e}")
            self.closeConnection()
            raise
        except BrokenPipeError:
            logging.warning(f"{self.peerAddr}: Connection broken during key exchange")
            raise
        except socket.timeout:
            logging.warning(f"{self.peerAddr}: Socket timed out during key exchange")
            raise

class ClientSecureConnection(SecureConnection):
    """
    Secure connection implementation for the client side.

    Args:
        socket (socket): socket object for the connection
        peerAddr ((str, int)): address of the peer (host, port)
        rsaKey (bytes): the server's public RSA key for encrypting the AES key
    """
    def __init__(self, socket, peerAddr, rsaKey):
        super().__init__(socket, peerAddr, rsaKey)

    def _performKeyExchange(self):
        """ Refer to base class documentation. """
        try:
            protocolMsg = self.recvRaw(constants.MESSAGE_SIZE).decode()
            logging.debug(f'{self.peerAddr}: Greeting recieved from server: {protocolMsg}')
            myProtocolMsg = 'FLITIFY_V' + constants.PROTOCOL_VERSION
            if protocolMsg != myProtocolMsg:
                raise ProtocolVersionError(f"My version is: {constants.PROTOCOL_VERSION}, server sent: {protocolMsg}")
            self.aes = cryptohelper.CryptoHelperAES()
            aesKey = self.aes.key
            encMsg = self.rsa.encrypt(aesKey)
            logging.debug(f"Sending AES key")
            self.sendRaw(encMsg)
            testMsg = self.recvEncrypted(constants.MESSAGE_SIZE)
            if testMsg != b'HNDSHK_PING':
                raise ValueError('Incorrect handshake message: {testMsg}')
            self.sendEncrypted(b'HNDSHK_PONG')
            logging.info(f"{self.peerAddr}: Client handshake finished")
        except ValueError as e:
            logging.error(f"{self.peerAddr}: Unexpected data format from server during handshake, closing connection: {e}")
            self.closeConnection()
            raise
        except BrokenPipeError:
            logging.warning(f"{self.peerAddr}: Connection broken by server during handshake")
            raise
        except ProtocolVersionError as e:
            logging.error(f"{self.peerAddr}: Protocol mismatch: {e}")
            self.closeConnection()
            raise
        except socket.timeout:
            logging.error(f"{self.peerAddr}: Client socket timed out during key exchange")
            raise
