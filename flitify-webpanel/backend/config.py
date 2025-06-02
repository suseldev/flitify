import json
import logging

class ConfigError(Exception):
    pass

def loadBackendConfig(config_path:str) -> dict:
    try:
        backend_config = open(config_path, 'r').read()
        backend_config = json.loads(backend_config)
        REQUIRED_KEYS = ['internal_api_host', 'db_address', 'db_user', 'db_password', 'db_name', 'host', 'port', 'jwt_secret', 'jwt_expiration_seconds']
        for key in REQUIRED_KEYS:
            if key not in backend_config:
                raise ValueError(f"backend config incorrect: missing key {key}")
        if  not backend_config['internal_api_host'].startswith('http://'):
            raise ValueError("invalid api host!")
        return backend_config
    except Exception as e:
        logging.critical("Failed to load server config: {e}")
        raise ConfigError(e)
