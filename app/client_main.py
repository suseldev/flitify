import logging
import socket

import config
from client.clientconnection import ClientConnection
from network.protocolconnection import ClientProtocolConnection

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



def main():
    # load config and key
    clientConfig = config.loadClientConfig()
    server_address = clientConfig['server_address']
    server_port = clientConfig['server_port']
    public_rsa_key = open(clientConfig['server_public_key_path'], 'rb').read()
    client_id = clientConfig['client_id']
    client_secret = clientConfig['client_secret']
    # setup connection
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((server_address, server_port))
    connection = ClientConnection(ClientProtocolConnection(clientSocket, (server_address, server_port), public_rsa_key, client_id, client_secret))

if __name__ == "__main__":
    main()
