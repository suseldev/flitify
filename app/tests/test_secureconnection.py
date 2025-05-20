import socket
import threading
import pytest
from Crypto.PublicKey import RSA
from network.secureconnection import ServerSecureConnection, ClientSecureConnection, ProtocolVersionError

@pytest.fixture(scope="module")
def rsa_keys():
    key = RSA.generate(2048)
    return key.export_key(), key.publickey().export_key()

@pytest.fixture
def server_socket():
    s = socket.socket()
    s.bind(("localhost", 0))
    s.listen(1)
    yield s
    s.close()

def run_server_with_socket(server_socket, rsa_key, server_ready_event):
    port = server_socket.getsockname()[1]
    server_ready_event.set()
    client_sock, addr = server_socket.accept()
    conn = ServerSecureConnection(client_sock, addr, rsa_key)
    conn.sendEncrypted(b"Hello from server!")
    msg_from_client = conn.recvEncrypted(1024)
    assert msg_from_client == b"Hello from client!"
    conn.closeConnection()

def run_server_with_invalid_protocol(server_socket, rsa_key, server_ready_event):
    from crypto.cryptohelper import CryptoHelperRSA
    port = server_socket.getsockname()[1]
    server_ready_event.set()
    client_sock, addr = server_socket.accept()
    conn = client_sock

    conn.send(b"FLITIFY_V213".ljust(32, b" "))
    try:
        rsa = CryptoHelperRSA(rsa_key)
        encKey = conn.recv(256)  # expected encrypted AES key size
        aes_key = rsa.decrypt(encKey)
        conn.close()
    except Exception:
        conn.close()

def test_full_secure_connection_handshake(rsa_keys, server_socket):
    rsa_private, rsa_public = rsa_keys
    server_ready_event = threading.Event()

    server_thread = threading.Thread(target=run_server_with_socket, args=(server_socket, rsa_private, server_ready_event))
    server_thread.start()

    server_ready_event.wait()
    port = server_socket.getsockname()[1]

    s = socket.socket()
    s.connect(("localhost", port))
    conn = ClientSecureConnection(s, ("localhost", port), rsa_public)
    msg_from_server = conn.recvEncrypted(1024)
    assert msg_from_server == b"Hello from server!"
    conn.sendEncrypted(b"Hello from client!")
    conn.closeConnection()
    s.close()

    server_thread.join()

def test_full_secure_connection_protocol_mismatch(rsa_keys, server_socket):
    rsa_private, rsa_public = rsa_keys
    server_ready_event = threading.Event()

    server_thread = threading.Thread(
        target=run_server_with_invalid_protocol,
        args=(server_socket, rsa_private, server_ready_event)
    )
    server_thread.start()

    server_ready_event.wait()
    port = server_socket.getsockname()[1]

    s = socket.socket()
    s.connect(("localhost", port))

    with pytest.raises(ProtocolVersionError):
        conn = ClientSecureConnection(s, ("localhost", port), rsa_public)

    s.close()
    server_thread.join()
