import logging

from network.baseconnection import BaseConnection
from crypto import cryptohelper

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


MESSAGE_SIZE = 8192

class SecureConnection(BaseConnection):
    def __init__(self, socket, peerAddr, rsaKey):
        super().__init__(socket, peerAddr)
        self.rsa = cryptohelper.CryptoHelperRSA(rsaKey)
        self.aes = None
        self._performKeyExchange()

    def _performKeyExchange():
        raise NotImplementedError()

    def sendEncrypted(self, data: bytes):
        data = self.aes.encrypt(data)
        self.sendRaw(data)

    def recvEncrypted(self, size: int) -> bytes:
        data = self.recvRaw(size)
        data = self.aes.decrypt(data)
        return data

class ServerSecureConnection(SecureConnection):
    def __init__(self, socket, peerAddr, rsaKey):
        super().__init__(socket, peerAddr, rsaKey)

    def _performKeyExchange(self):
        try:
            encMsg = self.recvRaw(MESSAGE_SIZE)
            aesKey = self.rsa.decrypt(encMsg)
            self.aes = cryptohelper.CryptoHelperAES(aesKey)
            logging.debug(f"{self.peerAddr}: AES key recieved")
            self.sendEncrypted(b'HNDSHK_PING')
            testMsg = self.recvEncrypted(MESSAGE_SIZE)
            if testMsg != b'HNDSHK_PONG':
                raise ValueError(f'Incorrect handshake message: {testMsg}')
            logging.info(f"{self.peerAddr}: Handshake finished")
        except ValueError as e:
            logging.warning(f"{self.peerAddr}: Unexpected data format during handshake, closing connection: {e}")
            self.closeConnection()
        except BrokenPipeError:
            logging.warning(f"{self.peerAddr}: Connection broken during handshake!")

class ClientSecureConnection(SecureConnection):
    def __init__(self, socket, peerAddr, rsaKey):
        super().__init__(socket, peerAddr, rsaKey)

    def _performKeyExchange(self):
        try:
            self.aes = cryptohelper.CryptoHelperAES()
            aesKey = self.aes.key
            encMsg = self.rsa.encrypt(aesKey)
            logging.debug(f"Sending AES key")
            self.sendRaw(encMsg)
            testMsg = self.recvEncrypted(MESSAGE_SIZE)
            if testMsg != b'HNDSHK_PING':
                raise ValueError('Incorrect handshake message: {testMsg}')
            self.sendEncrypted(b'HNDSHK_PONG')
            logging.info(f"{self.peerAddr}: Handshake finished")
        except ValueError as e:
            logging.warning(f"{self.peerAddr}: Unexpected data format during handshake, closing connection: {e}")
            self.closeConnection()
        except BrokenPipeError:
            logging.warning(f"{self.peerAddr}: Connection broken during handshake!")
