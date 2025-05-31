import platform
import logging
import os
import base64

from network.protocolconnection import ClientProtocolConnection
from client.OSAgents.linux import LinuxAgent

class ClientConnection():
    def __init__(self, connection:ClientProtocolConnection):
        self.connection = connection
        self.logger = logging.getLogger("flitifyclient")
        match platform.system():
            case "Linux":
                self.osagent = LinuxAgent()
            case "Windows":
                raise NotImplementedError("WindowsAgent not yet implemented")
            case _:
                raise NotImplementedError(f"Unsupported OS: {platform.system()}")
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
                case 'list_dir':
                    path = commandData.get('path', '/')
                    self.getDirectoryListing(path)
                case 'get_file':
                    if not 'path' in commandData:
                        raise ValueError("file_send: 'path' not found in server request")
                        self.connection.sendResponse('file_send', {'status': 'failed'})
                    self.sendFile(commandData['path'])
                case _:
                    self.connection.sendResponse('invalid_action', {})

    def getDirectoryListing(self, path:str):
        try:
            entries = self.osagent.getDirectoryListing(path)
            self.connection.sendResponse('list_dir', {'status': 'ok', 'entries': entries})
        except FileNotFoundError:
            self.connection.sendResponse('list_dir', {'status': 'not_found'})
        except Exception as e:
            self.logger.debug(f'{self.connection.peerAddr}: list_dir failed: {e}')
            self.connection.sendResponse('list_dir', {'status': 'failed'})

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

