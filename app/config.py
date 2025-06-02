import json
import logging

class ConfigError(Exception):
    pass

def loadServerConfig(config_path):
    try:
        server_config = open(config_path, 'r').read()
        server_config = json.loads(server_config)
        REQUIRED_KEYS = ['flitify_server', 'api_server']
        for key in REQUIRED_KEYS:
            if key not in server_config:
                raise ValueError(f"server config incorrect: missing key {key}")
        flitify_config = server_config['flitify_server']
        REQUIRED_FLITIFY_SERVER_KEYS = ['host', 'port', 'private_key_path', 'db_address', 'db_user', 'db_password', 'db_name']
        for key in REQUIRED_FLITIFY_SERVER_KEYS:
            if key not in flitify_config:
                raise ValueError(f"flitify_server config incorrect: missing key {key}")
        api_config = server_config['api_server']
        REQUIRED_API_SERVER_KEYS = ['host', 'port', 'secret']
        for key in REQUIRED_API_SERVER_KEYS:
            if key not in api_config:
                raise ValueError(f"api_server config incorrect: missing key {key}")
        return server_config
    except Exception as e:
        logging.critical(f"Failed to load server config: {e}")
        raise ConfigError(e)

def loadClientConfig(config_path='config_client.json'):
    try:
        client_config = open(config_path, 'r').read()
        client_config = json.loads(client_config)
        REQUIRED_KEYS = ['server_address', 'server_port', 'server_public_key_path', 'client_id', 'client_secret']
        for key in REQUIRED_KEYS:
            if key not in client_config:
                raise ValueError(f"Client config incorrect: missing key {key}")
        return client_config
    except Exception as e:
        logging.critical(f"Failed to load client config: {e}")
        raise ConfigError(e)
