from waitress import serve
from flask import Flask, abort, jsonify, request, make_response
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

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return "Hello World!"

        @self.app.route('/clients')
        def getOnlineClients():
            clientList = self.fserver.getClientList()
            return jsonify(clientList)

        @self.app.route('/<clientId>/status')
        def clientStatus(clientId: str):
            response_obj = {'status': 'ok', clientId: {}}
            client = self.fserver.getClientById(clientId)
            if not client:
                respnose = jsonify({'status': 'failed'})
                response.status_code = 404
                return response
            response_obj[clientId] = client.getClient().getStatus()
            return jsonify(response_obj)

        @self.app.route('/<clientId>/getfile')
        def getFile(clientId: str):
            filePath = request.args.get('file_path')
            client = self.fserver.getClientById(clientId)
            if not client:
                response = jsonify({'status': 'failed', 'details': 'Client not found'})
                response.status_code = 404
                return response
            client = client.getClient()
            if not filePath:
                response = jsonify({'status': 'failed', 'details': 'Invalid parameters'})
                response.status_code = 400
                return response
            try:
                file = client.getFile(filePath)
                if not file:
                    response = jsonify({'status': 'failed'})
                    response.status_code = 400 
                    return response
            except FileTransferError as e:
                response = jsonify({'status': 'failed', 'details': str(e)})
                response.status_code = 404
                return response
            response = make_response(file)
            response.headers.set('Content-Type', 'application/octet-stream')
            return response



    def start(self):
        serve(self.app, host=self.host, port=self.port)



