from network.secureconnection import ServerSecureConnection, ClientSecureConnection, SecureConnection
from storage.dbhandler import DBHandler
import constants

import logging
import abc
import json

class AuthenticationError(Exception):
    pass


class ServerProtocolConnection(ServerSecureConnection):
    def __init__(self, socket, peerAddr, rsaKey, dbHandler):
        super().__init__(socket, peerAddr, rsaKey)
        self.db = dbHandler
        self.clientId = None
        self._beginHandshake()

    def invokeAction(self, actionType: str, actionData: dict):
        payload = {
                "type": actionType,
                "data": actionData
        }
        jsonPayload = json.dumps(payload).encode()
        self.sendEncryptedLarge(jsonPayload)
        try:
            response = self.recvEncryptedLarge()
            response = json.loads(response)
            if 'type' not in response or 'data' not in response:
                raise ValueError("'type' or 'data' field not found in response")
            return response['type'], response['data']
        except json.JSONDecodeError:
            logging.warning("{self.peerAddr} ({self.clientId}): client sent invalid json")
        except ValueError as e:
            logging.warning("{self.peerAddr} ({self.clientId}): client sent invalid action response: {e}")



    def _beginHandshake(self):
        self.sendEncrypted(b'AUTH_REQUIRED')
        try:
            response = self.recvEncrypted(constants.MESSAGE_SIZE).decode()
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
                self.clientId = clientId
                logging.info(f'{self.peerAddr}: Authentication successful as {self.clientId}')
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

    def recvAction(self):
        try:
            action = self.recvEncryptedLarge()
            action = json.loads(action)
            if 'type' not in action or 'data' not in action:
                raise ValueError("'type' or 'data' field not found in action")
            return action['type'], action['data']
        except json.JSONDecodeError:
            logging.warning(f"{self.peerAddr} ({self.clientId}): server sent invalid json")
        except ValueError as e:
            logging.warning(f"{self.peerAddr}: client sent invalid action: {e}")

 
    def sendResponse(self, responseType: str, responseData: dict):
        payload = {
                "type": responseType,
                "data": responseData
        }
        jsonPayload = json.dumps(payload).encode()
        self.sendEncryptedLarge(jsonPayload)

    def _beginHandshake(self):
        try:
            command = self.recvEncrypted(constants.MESSAGE_SIZE).decode()
            if command != 'AUTH_REQUIRED':
                raise ValueError('Invalid auth prompt from server')
            authString = self.clientId + ':' + self.clientSecret
            self.sendEncrypted(authString.encode())
            response = self.recvEncrypted(constants.MESSAGE_SIZE).decode()
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
