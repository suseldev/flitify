from waitress import serve
from flask import g, Flask, abort, jsonify, request, make_response, Response, send_file
import logging
import os
from Crypto.PublicKey import RSA

from server.flitifyserver import FlitifyServer
from server.handlers.clienthandler import FileTransferError

class ApiServer:
    def __init__(self, server:FlitifyServer, host='localhost', port=37012, secret=None):
        """
        Initializes the internal API server.

        Args:
            server (FlitifyServer): An instance of FlitifyServer managing connected clients.
            host (str): Host address to bind the server to (defaults to 'localhost'). WARNING! Do not expose to public networks.
            port (int): Port number to listen to (defaults to 37012).
            secret (str, optional): API secret for request authentication.
        """
        self.fserver = server
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.api_secret = secret or os.getenv("API_SECRET", None)
        self.logger = logging.getLogger('apiserver')
        # Verifier decorator
        @self.app.before_request
        def verify_api_secret():
            if self.api_secret is None:
                return
            secret = request.headers.get('X-Api-Secret')
            if secret != self.api_secret:
                self.logger.warning(f"Unauthorized API access attempt from {request.remote_addr}")
                return jsonify({'request_status': 'failed', 'reason': 'unauthorized'}), 401
        self._setup_routes()

    def _getClient(self, clientId):
        """
        Retrieves a client instance by its identifier.

        Args:
            clientId (str): ID of the client.

        Returns:
            ClientHandler or None: The ClientHandler for a specific client if found, otherwise None.
        """
        client = self.fserver.getClientById(clientId)
        if client:
            return client.getClient()
        return None

    def _failWithReason(self, reason, error_code=400):
        """
        Constructs an error response with a given reason.

        Args:
            reason (str): Explanation of the error
            error_code (int): HTTP status code to return (defaults to 400).
        """
        response = jsonify({'request_status': 'failed', 'reason': reason})
        response.status_code = error_code
        return response

    def _setup_routes(self):
        """
        Sets up the API endpoint routes
        """
        @self.app.route('/')
        def index():
            return jsonify({'request_status': 'ok', 'details': 'api server online'})

        @self.app.route('/getkey')
        def getKey():
            key = RSA.importKey(self.fserver.rsaKey).public_key().export_key()
            response = Response(key)
            response.headers.set('Content-Type', 'application/octet-stream')
            response.headers.set('Content-Disposition', f'attachment; filename="pub_key.pem"')
            return response

        @self.app.route('/clients')
        def getOnlineClients():
            responseObj = {'status': 'ok', 'client_list': None}
            responseObj['client_list'] = self.fserver.getClientList()
            return jsonify(responseObj)

        @self.app.route('/<clientId>/status')
        def clientStatus(clientId: str):
            response_obj = {'request_status': 'ok', clientId: {}}
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
                return self._failWithReason('invalid parameters for getfile', error_code=400)
            try:
                fileContent = client.getFile(filePath)
                if not fileContent:
                    return self._failWithReason('unknown', error_code=504)
            except FileTransferError as e:
                return self._failWithReason('file transfer error', error_code=504)
            # Set response type to downloadable file
            response = Response(fileContent)
            response.headers.set('Content-Type', 'application/octet-stream')
            response.headers.set('Content-Disposition', f'attachment; filename="{filePath.split("/")[-1]}"')
            return response

        @self.app.route('/<clientId>/listdir')
        def listDirectory(clientId: str):
            path = request.args.get('path', '/')
            client = self._getClient(clientId)
            if not client:
                return self._failWithReason('client not found', error_code=404)
            entries = client.listDirectory(path)
            if entries is None:
                return self._failWithReason('client list_dir failed', error_code=500)
            return jsonify({'request_status': 'ok', 'entries': entries})

        @self.app.route('/<clientId>/shellcommand')
        def shellCommand(clientId: str):
            command = request.args.get('cmd')
            client = self._getClient(clientId)
            if not client:
                return self._failWithReason('client not found', error_code=404)
            timeout = request.args.get('timeout', None)
            if timeout != None:
                try:
                    timeout = int(timeout)
                except ValueError:
                    return self._failWithReason('invalid timeout', error_code=400)
            commandResponse = client.executeShellCommand(command, timeout=timeout)
            if commandResponse is None:
                return self._failWithReason('client shell_command failed', error_code=504)
            responseObj = {'stdout': commandResponse.get('stdout'), 'stderr': commandResponse.get('stderr')}
            return jsonify({'request_status': 'ok', 'command_response': responseObj})

        @self.app.route('/<clientId>/uploadfile', methods=['POST'])
        def uploadFile(clientId: str):
            if 'file' not in request.files or 'path' not in request.form:
                return self._failWithReason('Missing file or path', error_code=400)
            file = request.files['file']
            path = request.form['path']
            file_bytes = file.read()
            client = self._getClient(clientId)
            if not client:
                return self._failWithReason('client not found', error_code=404)
            success = client.uploadFile(path, file_bytes)
            if not success:
                return self._failWithReason('upload failed on client', error_code=504)
            return jsonify({'request_status': 'ok'})

    def start(self):
        """
        Starts the API server using the Waitress WSGI server.
        """
        serve(self.app, host=self.host, port=self.port)
