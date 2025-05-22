from waitress import serve
from flask import Flask
import logging

from server.flitifyserver import FlitifyServer

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

    def start(self):
        serve(self.app, host=self.host, port=self.port)



