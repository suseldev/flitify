from waitress import serve
from flask import Flask, request, jsonify, make_response, Response
import requests
import jwt

import os
import datetime
import logging

class FlitifyWebBackend:
    def __init__(self, dbHandler, jwt_secret:str, jwt_expiration_seconds:int, internal_api_host="http://localhost:37012", internal_api_secret=None, host="localhost", port="2137"):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.internal_api_secret = internal_api_secret or os.getenv("API_SECRET", None)
        self.internal_api_host = internal_api_host
        self.jwt_secret = jwt_secret
        self.jwt_expiration_seconds = jwt_expiration_seconds
        self.logger = logging.getLogger('backendapiserver')
        self.dbHandler = dbHandler
        self._setup_routes()

    def jwt_required(self, func):
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({'proxy_error': 'missing_token'}), 401
            token = auth_header.split(" ", 1)[1]
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
                request.user = payload['username']
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'token_expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'invalid_token'}), 401
            return func(*args, **kwargs)
        decorated.__name__ = func.__name__
        return decorated

    def _setup_routes(self):
        @self.app.route('/api/login', methods=['POST'])
        def login():
            data = request.json
            if not data or 'username' not in data or 'password' not in data:
                return jsonify({'login_status': 'missing_details'}), 400
            username = data['username']
            password = data['password']
            if not self.dbHandler or not self.dbHandler.loginUser(username, password):
                return jsonify({'login_status': 'invalid_credentials'}), 403
            token_payload = {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.jwt_expiration_seconds)
            }
            token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
            return jsonify({'login_status': 'ok', 'token': token})

        @self.app.route('/api/allclients', methods=['GET'])
        @self.jwt_required
        def list_clients():
            clients = list(self.dbHandler.secretsCollection.find({}, {"_id": 0}))
            return jsonify({'clients': clients})

        @self.app.route('/api/allclients', methods=['POST'])
        @self.jwt_required
        def create_client():
            data = request.json
            client_id = data.get("client_id")
            secret = data.get("secret")
            if not client_id or not secret:
                return jsonify({'proxy_status': 'missing_data'}), 400
            if not self.dbHandler.createClient(client_id, secret):
                return jsonify({'proxy_status': 'already_exists'}), 409
            return jsonify({'proxy_status': 'ok'}), 201

        @self.app.route('/api/allclients/<client_id>', methods=['PUT'])
        @self.jwt_required
        def update_client_secret(client_id):
            data = request.json
            new_secret = data.get("secret")
            if not new_secret:
                return jsonify({'proxy_status': 'missing_secret'}), 400
            if not self.dbHandler.changeClientSecret(client_id, new_secret):
                return jsonify({'proxy_status': 'not_found'}), 404
            return jsonify({'proxy_status': 'updated'})

        @self.app.route('/api/allclients/<client_id>', methods=['DELETE'])
        @self.jwt_required
        def delete_client(client_id):
            if not self.dbHandler.deleteClient(client_id):
                return jsonify({'proxy_status': 'not_found'}), 404
            return jsonify({'proxy_status': 'deleted'})

        @self.app.route('/api/users/change-password', methods=['POST'])
        @self.jwt_required
        def change_password():
            data = request.json
            new_password = data.get("newpassword")
            username = request.user
            if not new_password:
                return jsonify({'proxy_status': 'missing_password'}), 400
            if not self.dbHandler.changeUserPassword(username, new_password):
                return jsonify({'proxy_status': 'failed'}), 500
            return jsonify({'proxy_status': 'password_changed'})

        @self.app.route('/api/proxy/<path:proxied_path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        @self.jwt_required
        def proxy_to_internal(proxied_path):
            url = f"{self.internal_api_host}/{proxied_path}"
            headers = {key: value for key, value in request.headers if key != 'Host'}
            headers['X-Api-Secret'] = self.internal_api_secret or ''

            try:
                response = requests.request(
                    method=request.method,
                    url=url,
                    headers=headers,
                    data=request.get_data(),
                    cookies=request.cookies,
                    allow_redirects=False,
                    params=request.args
                )
                try:
                    content = response.json()
                    if isinstance(content, dict):
                        content['proxy_status'] = 'ok'
                        return make_response(jsonify(content), response.status_code)
                except ValueError:
                    pass
                for key, value in response.headers.items():
                    if key.lower() != 'content-encoding':
                        proxy_response.headers[key] = value
                return proxy_response
            except Exception as e:
                return jsonify({'proxy_status': 'failed'}), 500
    def start(self):
        serve(self.app, host=self.host, port=self.port)
