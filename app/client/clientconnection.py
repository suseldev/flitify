import platform
import logging
import os
import base64
import subprocess

from network.protocolconnection import ClientProtocolConnection
from client.OSAgents.linux import LinuxAgent

DEFAULT_TIMEOUT=5

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
                    status_dict = self.osagent.getStatus()
                    self.connection.sendResponse('status', status_dict)
                case 'list_dir':
                    path = commandData.get('path', '/')
                    self.getDirectoryListing(path)
                case 'shell_command':
                    command = commandData.get('command')
                    if not command:
                        self.connection.sendResponse('shell_response', {'status': 'failed'})
                        raise ValueError("shell_command: command not found in server request")
                    timeout = commandData.get('timeout', DEFAULT_TIMEOUT)
                    self.executeShellCommand(command, timeout=timeout)
                case 'get_file':
                    if not 'path' in commandData:
                        self.connection.sendResponse('file_send', {'status': 'failed'})
                        raise ValueError("file_send: 'path' not found in server request")
                    self.sendFile(commandData['path'])
                case 'upload_file':
                    path = commandData.get('path')
                    filedata = commandData.get('filedata')
                    if not path or not filedata:
                        raise ValueError("upload_file: 'path' or 'filedata' missing")
                    self.saveFile(path, filedata)
                case _:
                    self.connection.sendResponse('invalid_action', {})

    def getDirectoryListing(self, path:str):
        try:
            entries = self.osagent.getDirectoryListing(path)
            self.connection.sendResponse('list_dir', {'status': 'ok', 'entries': entries})
        except FileNotFoundError:
            self.connection.sendResponse('list_dir', {'status': 'not_found'})
            return
        except Exception as e:
            self.connection.sendResponse('list_dir', {'status': 'failed'})
            self.logger.warning(f'{self.connection.peerAddr}: list_dir failed: {e}')

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
            self.logger.warning(f'{self.connection.peerAddr}: file_send failed: {e}')

    def saveFile(self, path: str, base64data: str):
        try:
            file_bytes = base64.b64decode(base64data)
            if os.path.exists(path):
                self.connection.sendResponse('file_upload', {'status': 'file_exists'})
                return
            with open(path, 'wb') as f:
                f.write(file_bytes)
            self.connection.sendResponse('file_upload', {'status': 'ok'})
        except Exception as e:
            self.connection.sendResponse('file_upload', {'status': 'failed'})
            self.logger.warning(f'{self.connection.peerAddr}: file_upload failed: {e}')

    def executeShellCommand(self, command: str, timeout=DEFAULT_TIMEOUT):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
            self.connection.sendResponse('shell_result', {'status': 'ok', 'stdout': result.stdout, 'stderr': result.stderr, 'exitcode': result.returncode})
        except subprocess.TimeoutExpired:
            self.connection.sendResponse('shell_result', {'status': 'timeout', 'stderr': 'Command timed out', 'exitcode': -1})
            return
        except Exception as e:
            self.connection.sendResponse('shell_result', {'status': 'failed'})
            self.logger.warning(f'{self.connection.peerAddr}: shell_command failed: {e}')

