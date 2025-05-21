from network.protocolconnection import ClientProtocolConnection

class ClientConnection():
    def __init__(self, connection:ClientProtocolConnection):
        self.connection = connection
        self._actionLoop()

    def _actionLoop(self):
        while True:
            if not self.connection.running:
                self.logging.info(f'{self.connection.peerAddr}: connection closed during actionLoop')
                break
            command, commandData = self.connection.recvAction()
            match command:
                case 'ping':
                    self.connection.sendResponse('pong', {})
                case 'get_status':
                    self.connection.sendResponse('status', status_dict)

