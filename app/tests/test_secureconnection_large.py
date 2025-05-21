import socket
import threading
import pytest

from network.secureconnection import ServerSecureConnection, ClientSecureConnection


@pytest.fixture
def rsa_keys():
    from Crypto.PublicKey import RSA
    key = RSA.generate(2048)
    return key.export_key(), key.publickey().export_key()


@pytest.fixture
def server_socket():
    s = socket.socket()
    s.bind(("localhost", 0))
    s.listen(1)
    yield s
    s.close()


def run_server(server_sock, rsa_private, server_ready_event, data_expected):
    port = server_sock.getsockname()[1]
    server_ready_event.set()
    client_sock, addr = server_sock.accept()

    server_conn = ServerSecureConnection(client_sock, addr, rsa_private)
    received = server_conn.recvEncryptedLarge()
    assert received == data_expected
    server_conn.closeConnection()


def test_send_recv_encrypted_large(rsa_keys, server_socket):
    rsa_private, rsa_public = rsa_keys
    server_ready_event = threading.Event()
    test_data = b"x" * 50_000  # 50 KB danych do testu

    server_thread = threading.Thread(
        target=run_server, args=(server_socket, rsa_private, server_ready_event, test_data)
    )
    server_thread.start()

    server_ready_event.wait()
    port = server_socket.getsockname()[1]

    client_sock = socket.socket()
    client_sock.connect(("localhost", port))
    client_conn = ClientSecureConnection(client_sock, ("localhost", port), rsa_public)

    client_conn.sendEncryptedLarge(test_data)
    client_conn.closeConnection()
    client_sock.close()

    server_thread.join()
