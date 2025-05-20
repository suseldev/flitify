from network.secureconnection import ServerSecureConnection, ClientSecureConnection
from storage.dbhandler import DBHandler
import logging

class AuthenticationError(Exception):
    pass

class ServerProtocolConnection(ServerSecureConnection):
    def __init__(self, socket, peerAddr, rsaKey, dbHandler):
        super().__init__(socket, peerAddr, rsaKey)
        self.db = dbHandler
        self._beginHandshake()

    def _beginHandshake(self):
        self.sendEncrypted(b'AUTH_REQUIRED')
        try:
            response = self.recvEncrypted(self.MESSAGE_SIZE).decode()
            response = response.split(':')
            if len(response) != 2:
                raise ValueError('Invalid data format')
            clientId = response[0]
            secret = response[1]
            if secret is None:
                self.sendEncrypted(b'AUTH_INVALID')
                raise AuthenticationError('No secret given')
            if secret != self.db.getSharedSecret(clientId):
                self.sendEncrypted(b'AUTH_INVALID')
                raise AuthenticationError('Incorrect secret or hostname')
            else:
                self.sendEncrypted(b'AUTH_CORRECT')
                loging.info(f'{self.peerAddr}: Authentication successful')
        except ValueError as e:
            logging.warning(f'{self.peerAddr}: Error while authenticating: {e}')
            self.closeConnection()
            raise
        except AuthenticationError as e:
            logging.warning(f'{self.peerAddr}: Authentication error: {e}')
            self.closeConnection()
            raise

class ClientProtocolConnection(ClientSecureConnection):
    def __init__(self, socket, peerAddr, rsaKey, clientId, clientSecret):
        super().__init__(socket, peerAddr, rsaKey)
        self.clientId = clientId
        self.clientSecret = clientSecret
        self._beginHandshake()

    def _beginHandshake(self):
        try:
            command = self.recvEncrypted(self.MESSAGE_SIZE).decode()
            if command != 'AUTH_REQUIRED':
                raise ValueError('Invalid auth prompt from server')
            authString = self.clientId + ':' + self.clientSecret
            self.sendEncrypted(authString.encode())
            response = self.recvEncrypted(self.MESSAGE_SIZE).decode()
            if response == 'AUTH_INVALID':
                raise AuthenticationError('Incorrect secret or hostname')
            if response == 'AUTH_CORRECT':
                logging.info(f'{self.peerAddr}: Client authentication successful')
        except ValueError as e:
            logging.error(f'{self.peerAddr}: Invalid data from server: {e}')
            self.closeConnection()
            raise
        except AuthenticationError as e:
            logging.error(f'{self.peerAddr}: Client authentication error: {e}')
            self.closeConnection()
            raise
