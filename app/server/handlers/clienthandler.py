from network.protocolconnection import ServerProtocolConnection

class ClientHandler():
    def __init__(self, connection: ServerProtocolConnection):
        self.connection = connection
        self.clientId = connection.clientId

    def ping(self):
        resp_type, resp_contents = self.connection.invokeAction(actionType, data)
        try:
            if resp_type != 'pong':
                raise ValueError('invalid response from client for ping: {resp_type}')
            return True
        except ValueError as e:
            logging.warning('{self.connection.peerAddr} ({self.clientId}): ping failed: {e}') 

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
