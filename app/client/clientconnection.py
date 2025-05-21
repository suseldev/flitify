import logging

from network.protocolconnection import ClientProtocolConnection

class ClientConnection():
    def __init__(self, connection:ClientProtocolConnection):
        self.connection = connection
        self._actionLoop()

    def _actionLoop(self):
        while True:
            if not self.connection.running:
                logging.error(f'{self.connection.peerAddr}: connection closed during actionLoop')
                break
            command, commandData = self.connection.recvAction()
            logging.debug(f'{self.connection.peerAddr}: received command {command}')
            match command:
                case 'ping':
                    self.connection.sendResponse('pong', {})
                case 'get_status':
                    status_dict = {'cpu': 36, 'ram': 48}
                    self.connection.sendResponse('status', status_dict)

