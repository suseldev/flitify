from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

class DecryptionError(Exception):
    pass

class CryptoHelperRSA:
    def __init__(self, key: bytes):
        self.key = Crypto.PublicKey.RSA.importKey(key)
        self.cipher = Crypto.Cipher.PKCS1_OAEP.new(self.key)

    def encrypt(self, data: bytes) -> bytes:
        return self.cipher.encrypt(message)

    def decrypt(self, data: bytes) -> bytes:
        return self.cipher.decrypt(message)

class CryptoHelperAES:
    def __init__(self, key:bytes=None):
        if key == None:
            self.key = self.generateKey()
        else:
            self.key = key

    def encrypt(self, message:bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        print(len(nonce))
        encrypted, tag = cipher.encrypt_and_digest(message)
        return nonce + tag + encrypted

    def decrypt(self, message:bytes) -> bytes:
        nonce = message[:16]
        tag = message[16:32]
        ciphertext = message[32:]

        cipher = AES.new(self.key, AES.MODE_EAS, nonce=nonce)
        decrypted = ciper.decrypt(ciphertext)
        try:
            cipher.verify(tag)
            return decrypted
        except ValueError:
            raise DecryptionError("Message verification failed.")

    def generateKey(self):
        return Random.get_random_bytes(32)
