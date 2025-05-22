from network.secureconnection import ServerSecureConnection, ClientSecureConnection, SecureConnection
from storage.dbhandler import DBHandler
import constants

import logging
import json
import threading
import socket

class AuthenticationError(Exception):
    pass


class ServerProtocolConnection(ServerSecureConnection):
    def __init__(self, socket, peerAddr, rsaKey, dbHandler):
        super().__init__(socket, peerAddr, rsaKey)
        self.db = dbHandler
        self.clientId = None
        self.sendLock = threading.Lock()
        self.authenticated = False
        self._beginHandshake()


    def closeConnectionWithReason(self, reason):
        try:
            payload = {
                    "type": 'kick',
                    "data": {'reason': reason}
            }
            jsonPayload = json.dumps(payload).encode()
            self.sendEncryptedLarge(jsonPayload)
        except Exception as e:
            self.logger.warning(f'{self.peerAddr} ({self.clientId or "unknown"}): failed to close connection gracefully: {e}')
        self.closeConnection()
        self.logger.debug(f"{self.peerAddr} ({self.clientId or 'unknown'}): connection closed with reason {reason}")

    def invokeAction(self, actionType: str, actionData: dict):
        with self.sendLock:
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
                if response['type'] == 'invalid_action':
                    raise ValueError("client sent 'invalid_action'")
                return response['type'], response['data']
            except json.JSONDecodeError:
                self.logger.warning(f"{self.peerAddr} ({self.clientId}): client sent invalid json")
            except ValueError as e:
                self.logger.warning(f"{self.peerAddr} ({self.clientId}): client sent invalid action response: {e}")



    def _beginHandshake(self):
        if not self.running:
            return
        try:
            self.sendEncrypted(b'AUTH_REQUIRED')
            response = self.recvEncrypted(constants.MESSAGE_SIZE).decode()
            response = response.split(':')
            if len(response) != 2:
                raise ValueError('Invalid data format')
            clientId = response[0]
            secret = response[1]
            if secret is None:
                self.sendEncrypted(b'AUTH_INVALID')
                raise AuthenticationError('secret not found for id: {clientId}')
            if secret != self.db.getSharedSecret(clientId):
                self.sendEncrypted(b'AUTH_INVALID')
                raise AuthenticationError('Incorrect secret or hostname')
            else:
                self.sendEncrypted(b'AUTH_CORRECT')
                self.clientId = clientId
                self.authenticated = True
                self.logger.info(f'{self.peerAddr}: Authentication successful as {self.clientId}')
        except ValueError as e:
            self.logger.warning(f'{self.peerAddr}: Error while authenticating: {e}')
            self.closeConnection()
        except AuthenticationError as e:
            self.logger.warning(f'{self.peerAddr}: Authentication error: {e}')
            self.closeConnectionWithReason(f'Authentication error: {e}')
        except socket.timeout:
            self.logger.warning(f'{self.peerAddr}: Connection timed out during authentication')
            self.closeConnection()
        except Exception as e:
            self.logger.error(f'{self.peerAddr}: Uncaught exception during authentication: {e}')
            self.closeConnection()

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
            self.logger.warning(f"{self.peerAddr} ({self.clientId}): Server sent invalid json")
        except ValueError as e:
            self.logger.warning(f"{self.peerAddr}: Client sent invalid action: {e}")

 
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
                self.logger.info(f'{self.peerAddr}: Client authentication successful')
        except ValueError as e:
            self.logger.error(f'{self.peerAddr}: Invalid data from server: {e}')
            self.closeConnection()
        except AuthenticationError as e:
            self.logger.error(f'{self.peerAddr}: Client authentication error: {e}')
            self.closeConnection()
