import logging
import os
import base64

from network.protocolconnection import ClientProtocolConnection

class ClientConnection():
    def __init__(self, connection:ClientProtocolConnection):
        self.connection = connection
        self.logger = logging.getLogger("flitifyclient")
        self._actionLoop()

    def _actionLoop(self):
        while True:
            if not self.connection.running:
                self.logger.error(f'{self.connection.peerAddr}: connection closed during actionLoop')
                break
            command, commandData = self.connection.recvAction()
            self.logger.debug(f'{self.connection.peerAddr}: received command {command}')
            match command:
                case 'kick':
                    if 'reason' not in commandData:
                        raise ValueError('kicked without reason')
                    self.logger.error(f"{self.connection.peerAddr}: kicked by server: {commandData['reason']}")
                    self.connection.closeConnection()
                    return
                case 'ping':
                    self.connection.sendResponse('pong', {})
                case 'get_status':
                    status_dict = {'cpu': 36, 'ram': 48}
                    self.connection.sendResponse('status', status_dict)
                case 'get_file':
                    if not 'path' in commandData:
                        raise ValueError("file_send: 'path' not found in server request")
                        self.connection.sendResponse('file_send', {'status': 'failed'})
                    self.sendFile(commandData['path'])
                case _:
                    self.connection.sendResponse('invalid_action', {})

    def sendFile(self, path:str):
        try:
            if not os.path.isfile(path):
                self.connection.sendResponse('file_send', {'status': 'not_found'})
                return
            fileData = open(path, 'rb').read()
            fileData = base64.b64encode(fileData).decode()
            self.connection.sendResponse('file_send', {'status': 'ok', 'filedata': fileData})
        except Exception as e:
            self.connection.sendResponse('file_send', {'status': 'failed'})
            self.logger.debug(f'{self.connection.peerAddr}: file_send failed: {e}')

