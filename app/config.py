def loadServerConfig():
    config = {'host': '127.0.0.1', 'port': 2137, 'private_key_path': 'privkey.pem'}
    return config

def loadClientConfig():
    config = {'server_address': 'localhost', 'server_port': 2137, 'server_public_key_path': 'pubkey.pem', 'client_id': 'TEST-1', 'client_secret':'abcdefgh'}
    return config
