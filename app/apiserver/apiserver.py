from waitress import serve
from flask import g, Flask, abort, jsonify, request, make_response
import logging

from server.flitifyserver import FlitifyServer
from server.handlers.clienthandler import FileTransferError

class ApiServer:
    def __init__(self, server:FlitifyServer, host='localhost', port=37012):
        self.fserver = server
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self._setup_routes()

    def _getClient(self, clientId):
        client = self.fserver.getClientById(clientId)
        if client:
            return client.getClient()
        return None

    def _failWithReason(self, reason, error_code=400):
        response = jsonify({'status': 'failed', 'reason': reason})
        response.status_code = error_code
        return response

    def _setup_routes(self):
        # API specification: 404 = object not found; 418 (I'm a teapot): client failed
        @self.app.route('/')
        def index():
            return jsonify({'status': 'ok', 'details': 'api server online'})

        @self.app.route('/clients')
        def getOnlineClients():
            clientList = self.fserver.getClientList()
            return jsonify(clientList)

        @self.app.route('/<clientId>/status')
        def clientStatus(clientId: str):
            response_obj = {'status': 'ok', clientId: {}}
            client = self._getClient(clientId)
            if not client:
                return self._failWithReason('client not found', error_code=404)
            response_obj[clientId] = client.getStatus()
            return jsonify(response_obj)

        @self.app.route('/<clientId>/getfile')
        def getFile(clientId: str):
            filePath = request.args.get('file_path')
            client = self._getClient(clientId)
            if not client:
                return self._failWithReason('client not found', error_code=404)
            if not filePath:
                return self._failWithReason('invalid parameters for getfile', 400)
            try:
                file = client.getFile(filePath)
                if not file:
                    return self._failWithReason('unknown', error_code=504)
            except FileTransferError as e:
                return self._failWithReason('file transfer error', error_code=504)
            response.headers.set('Content-Type', 'application/octet-stream')
            return response



    def start(self):
        serve(self.app, host=self.host, port=self.port)
