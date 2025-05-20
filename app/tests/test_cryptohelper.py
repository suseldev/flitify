import pytest
from Crypto.PublicKey import RSA
from crypto.cryptohelper import CryptoHelperRSA, CryptoHelperAES, DecryptionError

def test_aes_encrypt_decrypt():
    aes = CryptoHelperAES()
    plaintext = b"Test message for AES"
    encrypted = aes.encrypt(plaintext)
    decrypted = aes.decrypt(encrypted)
    assert decrypted == plaintext

def test_aes_decrypt_with_wrong_tag():
    aes = CryptoHelperAES()
    plaintext = b"Test message for AES"
    # Corrupt tag
    encrypted = bytearray(aes.encrypt(plaintext))
    encrypted[20] ^= 0xFF
    with pytest.raises(DecryptionError):
        aes.decrypt(bytes(encrypted))

def test_rsa_encrypt_decrypt():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    rsa_enc = CryptoHelperRSA(public_key)
    rsa_dec = CryptoHelperRSA(private_key)
    plaintext = b"Test message for RSA"
    encrypted = rsa_enc.encrypt(plaintext)
    decrypted = rsa_dec.decrypt(encrypted)
    assert decrypted == plaintext

def test_rsa_decrypt_with_wrong_key():
    key1 = RSA.generate(2048)
    key2 = RSA.generate(2048)
    rsa_enc = CryptoHelperRSA(key1.publickey().export_key())
    rsa_dec = CryptoHelperRSA(key2.export_key())
    plaintext = b"Test message for RSA"
    encrypted = rsa_enc.encrypt(plaintext)
    with pytest.raises(ValueError):
        rsa_dec.decrypt(encrypted)
