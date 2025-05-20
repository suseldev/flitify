import socket
import threading
import time
import pytest
from Crypto.PublicKey import RSA
from unittest.mock import MagicMock

from network.protocolconnection import ServerProtocolConnection, ClientProtocolConnection, AuthenticationError
from network.secureconnection import ClientSecureConnection

MESSAGE_SIZE = 1024


@pytest.fixture(scope="module")
def rsa_keypair():
    key = RSA.generate(2048)
    return key.export_key(), key.export_key()


class DummyDB:
    def __init__(self, secrets):
        self.secrets = secrets

    def getSharedSecret(self, client_id):
        return self.secrets.get(client_id, None)


def server_thread(listener_sock, rsa_private_key, db_handler):
    client_sock, addr = listener_sock.accept()
    try:
        conn = ServerProtocolConnection(client_sock, addr, rsa_private_key, db_handler)
        while conn.running:
            time.sleep(0.1)
    except Exception:
        pass
    finally:
        client_sock.close()


def test_successful_authentication(rsa_keypair):
    rsa_private_key, rsa_public_key = rsa_keypair
    db = DummyDB({"client1": "correct_secret"})

    # Setup server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('localhost', 0))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    # Start server thread
    thread = threading.Thread(target=server_thread, args=(server_sock, rsa_private_key, db))
    thread.daemon = True
    thread.start()

    # Client side socket
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('localhost', port))

    # Use ClientProtocolConnection with correct credentials
    client_conn = ClientProtocolConnection(client_sock, ('localhost', port), rsa_public_key, "client1", "correct_secret")

    # If handshake succeeds, connection should remain open
    assert client_conn.running is True

    # Cleanup
    client_sock.close()
    server_sock.close()
    thread.join(timeout=1)


def test_failed_authentication_wrong_secret(rsa_keypair):
    rsa_private_key, rsa_public_key = rsa_keypair
    db = DummyDB({"client1": "correct_secret"})

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('localhost', 0))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    thread = threading.Thread(target=server_thread, args=(server_sock, rsa_private_key, db))
    thread.daemon = True
    thread.start()

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('localhost', port))

    with pytest.raises(AuthenticationError):
        # Use wrong secret to provoke AuthenticationError
        ClientProtocolConnection(client_sock, ('localhost', port), rsa_public_key, "client1", "wrong_secret")

    client_sock.close()
    server_sock.close()
    thread.join(timeout=1)


def test_failed_authentication_invalid_format(rsa_keypair):
    rsa_private_key, rsa_public_key = rsa_keypair
    db = DummyDB({"client1": "correct_secret"})

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('localhost', 0))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    thread = threading.Thread(target=server_thread, args=(server_sock, rsa_private_key, db))
    thread.daemon = True
    thread.start()

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('localhost', port))

    clientCon = ClientSecureConnection(client_sock, ('localhost', port), rsa_public_key)
    auth_req = clientCon.recvEncrypted(MESSAGE_SIZE)
    assert auth_req == b'AUTH_REQUIRED'
    invalid_data = 'client::'
    clientCon.sendEncrypted(invalid_data.encode())
    with pytest.raises(BrokenPipeError):
        auth_resp = clientCon.recvEncrypted(MESSAGE_SIZE)
        assert auth_resp == b'AUTH_INVALID'

    client_sock.close()
    server_sock.close()
    thread.join(timeout=1)

