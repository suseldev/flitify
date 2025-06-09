import threading
import time
import logging
import base64
import socket

import constants
from network.protocolconnection import ServerProtocolConnection
from server.handlers.clientutils import disable_timeout

class FileTransferError(Exception):
    pass

class InvalidResponseError(ValueError):
    pass

class ClientHandler():
    def __init__(self, connection: ServerProtocolConnection):
        self.connection = connection
        self.clientId = connection.clientId
        self._startKeepAliveLoop()
    
    def getConnection(self):
        return self.connection

    def isOnline(self):
        if self.connection.sendLock.locked():
            return True 
        return self.ping()

    def ping(self):
        actionType = 'ping'
        data = {}
        try:
            resp_type, resp_contents = self.connection.invokeAction(actionType, data)
            if resp_type != 'pong':
                raise InvalidResponseError(f'invalid response from client for ping: {resp_type}: {resp_contents}')
            return True
        except InvalidResponseError as e:
            logging.warning(f'{self.connection.peerAddr} ({self.clientId}): Ping failed: {e}') 
            self.closeConnectionWithReason('invalid_response')
        except BrokenPipeError:
            logging.info(f'{self.connection.peerAddr} ({self.clientId}): Connection closed')

    def getStatus(self):
        actionType = 'get_status'
        data = {} 
        try:
            resp_type, resp_contents = self.connection.invokeAction(actionType, data)
            if resp_type != 'status':
                raise InvalidResponseError(f'invalid response type from client for get_status: {resp_type}')
            return resp_contents
        except InvalidResponseError as e:
            logging.warning('{self.connection.peerAddr} ({self.clientId}): get_status failed: {e}') 
            self.closeConnectionWithReason('invalid_response')

    @disable_timeout()
    def getFile(self, path: str):
        actionType = 'get_file'
        data = {'path': path}
        try:
            logging.debug('Waiting for file...')
            resp_type, resp_contents = self.connection.invokeAction(actionType, data)
            if resp_type != 'file_send':
                raise InvalidResponseError(f'invalid response type from client for get_file: {resp_type}')
            if 'status' not in resp_contents:
                raise InvalidResponseError("'status' not found in client response")
            if resp_contents['status'] == 'not_found':
                raise FileTransferError("Invalid path")
            elif resp_contents['status'] == 'failed':
                raise FileTransferError('Client responded with failed status')
            if 'filedata' not in resp_contents:
                raise InvalidResponseError("'filedata' not found in client response")
            filebytes = base64.b64decode(resp_contents['filedata'])
            # TODO: Validate checksum
            return filebytes
        except InvalidResponseError as e:
            logging.warning(f'{self.connection.peerAddr} ({self.clientId}): get_file failed (InvalidResponseError): {e}') 
            self.closeConnectionWithReason('invalid_response')
        except FileTransferError as e:
            logging.info(f'{self.connection.peerAddr} ({self.clientId}): get_file failed (FileTransferError): {e}')

    @disable_timeout()
    def uploadFile(self, path: str, file_bytes: bytes):
        try:
            data = {'path': path, 'filedata': base64.b64encode(file_bytes).decode()}
            resp_type, resp = self.connection.invokeAction('upload_file', data)
            if resp_type != 'file_upload':
                raise InvalidResponseError(f'invalid response type: {resp_type}')
            return resp.get('status') == 'ok'
        except InvalidResponseError as e:
            logging.warning(f'{self.connection.peerAddr} ({self.clientId}): upload_file failed (invalid response)')
            self.closeConnectionWithReason('invalid_response')
        except Exception as e:
            logging.warning(f'{self.connection.peerAddr} ({self.clientId}): upload_file failed: {e}')

    def listDirectory(self, path: str) -> list | None:
        actionType = 'list_dir'
        data = {'path': path}
        try:
            resp_type, resp_contents = self.connection.invokeAction(actionType, data)
            if resp_type != 'list_dir':
                raise InvalidResponseError(f'invalid response type from client for list_dir: {resp_type}')
            if resp_contents.get('status') != 'ok':
                raise InvalidResponseError(f"list_dir failed: {resp_contents.get('status')}")
            return resp_contents['entries']
        except InvalidResponseError as e:
            logging.warning(f'{self.connection.peerAddr} ({self.clientId}): list_dir failed (InvalidResponseError): {e}') 
            self.closeConnectionWithReason('invalid_response')
        except Exception as e:
            logging.warning(f'{self.connection.peerAddr} ({self.clientId}): listDirectory failed: {e}')

    @disable_timeout()
    def executeShellCommand(self, command: str, timeout=None):
        actionType = 'shell_command'
        if not timeout is None:
            data = {'command': command, 'timeout': timeout}
        else:
            data = {'command': command}
        try:
            resp_type, resp_contents = self.connection.invokeAction(actionType, data)
            if resp_type != 'shell_result':
                raise InvalidResponseError(f'invalid response type from client for shell_command: {resp_type}')
            if resp_contents.get('status') == 'timeout':
                return resp_contents
            if resp_contents.get('status') != 'ok':
                raise InvalidResponseError(f'shell_command failed: {resp_contents.get("status")}')
            return resp_contents
        except InvalidResponseError as e:
            logging.warning(f'{self.connection.peerAddr} ({self.clientId}): shell_command failed (InvalidResponseError): {e}') 
            self.closeConnectionWithReason('invalid_response')
        except Exception as e:
            logging.error(f'{self.connection.peerAddr} ({self.clientId}): shell_command failed: {e}')

    def _keepAliveLoop(self, interval=constants.INTERVAL):
        if not self.connection.running:
            return
        logging.debug(f'{self.connection.peerAddr} ({self.clientId}): keepAliveLoop started')
        while True:
            if not self.connection.running:
                return
            time.sleep(interval)
            if self.connection.sendLock.locked():
                continue
            try:
                self.ping()
            except socket.timeout:
                logging.error(f'{self.connection.peerAddr} ({self.clientId}): Connection timed out')
                self.connection.closeConnection()
            except Exception as e:
                logging.error(f'{self.connection.peerAddr} ({self.clientId}): Uncaught exception in keepAliveLoop: {e}')
                self.connection.closeConnection()

    def _startKeepAliveLoop(self):
        threading.Thread(target=self._keepAliveLoop, daemon=True).start()


