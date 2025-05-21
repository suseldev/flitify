import threading
import time
import logging

from network.protocolconnection import ServerProtocolConnection
import base64

class FileTransferError(Exception):
    pass

class ClientHandler():
    def __init__(self, connection: ServerProtocolConnection):
        self.connection = connection
        self.clientId = connection.clientId
        self._startKeepAliveLoop()
    
    def isOnline(self):
        if not self.connection.sendLock.locked():
            return True 
        return self.ping()

    def ping(self):
        actionType = 'ping'
        data = {}
        try:
            resp_type, resp_contents = self.connection.invokeAction(actionType, data)
            if resp_type != 'pong':
                raise ValueError('invalid response from client for ping: {resp_type}')
            return True
        except ValueError as e:
            logging.warning(f'{self.connection.peerAddr} ({self.clientId}): ping failed: {e}') 
        except BrokenPipeError:
            logging.info(f'{self.connection.peerAddr} ({self.clientId}): connection closed by remote host')

    def getStatus(self):
        actionType = 'get_status'
        data = {} 
        try:
            resp_type, resp_contents = self.connection.invokeAction(actionType, data)
            if resp_type != 'status':
                raise ValueError(f'invalid response type from client for get_status: {resp_type}')
            return resp_contents
        except ValueError as e:
            logging.warning('{self.connection.peerAddr} ({self.clientId}): get_status failed: {e}') 

    def getFile(self, path: str):
        actionType = 'get_file'
        data = {'path': path}
        try:
            logging.debug('Waiting for file...')
            resp_type, resp_contents = self.connection.invokeAction(actionType, data)
            if resp_type != 'file_send':
                raise ValueError(f'invalid response type from client for get_file: {resp_type}')
            if 'status' not in resp_contents:
                raise ValueError("'status' not found in client response")
            if resp_contents['status'] == 'not_found':
                raise FileTransferError("Invalid path")
            elif resp_contents['status'] == 'failed':
                raise FileTransferError('Client responded with failed status')
            if 'filedata' not in resp_contents:
                raise ValueError("'filedata' not found in client response")
            filebytes = base64.b64decode(resp_contents['filedata'])
            # TODO: Validate checksum
            return filebytes
        except ValueError as e:
            logging.warning('{self.connection.peerAddr} ({self.clientId}): get_file failed: {e}') 
    def _keepAliveLoop(self, interval=5):
        logging.debug(f'{self.connection.peerAddr} ({self.clientId}): keepAliveLoop started')
        while self.connection.running:
            time.sleep(interval)
            if self.connection.sendLock.locked():
                continue
            try:
                self.ping()
            except Exception as e:
                logging.error(f'{self.connection.peerAddr} ({self.clientId}): uncaught exception in keepAliveLoop: {e}')
                self.connection.closeConnection()

    def _startKeepAliveLoop(self):
        threading.Thread(target=self._keepAliveLoop, daemon=True).start()
