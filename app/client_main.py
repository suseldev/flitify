import logging
import socket
import logging
import time

import config
import constants
from config import ConfigError
from client.clientconnection import ClientConnection, ConnectionKickedError
from network.protocolconnection import ClientProtocolConnection, AuthenticationError

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



def clientStartup():
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

def mainLoop():
    invalid_attempts = 0
    while True:
        if invalid_attempts > 5:
            break
            return
        try:
            clientStartup()
        except BrokenPipeError as e:
            logging.error(f"Connection closed: broken pipe: {e}")
        except ConnectionRefusedError:
            logging.error("Connection refused")
        except KeyboardInterrupt:
            logging.info("Shutting down client, keyboard interrupt")
            break
            return
        except AuthenticationError as e:
            logging.error(f"Connection closed: AuthenticationError: {e}")
            invalid_attempts += 1
        except ConfigError:
            logging.error(f"Cannot start: invalid config")
            return 1
            break
        except ConnectionKickedError as e:
            pass

        time.sleep(constants.CLIENT_RECONNECT_TIME)


if __name__ == "__main__":
    mainLoop()
   
