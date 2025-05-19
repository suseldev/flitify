from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA

class DecryptionError(Exception):
    """ Exception raised when decryption fails (for example due to data authentication failiure) """
    pass

class CryptoHelperRSA:
    """
    RSA encryption and decryption helper.

    Args:
        key (bytes): Exported RSA key to be imported
    """

    def __init__(self, key: bytes):
        self.key = RSA.importKey(key)
        self.cipher = PKCS1_OAEP.new(self.key)

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypts data using the RSA key
        
        Args:
            data (bytes): Plaintext data to encrypt
        
        Returns:
            bytes: Encrypted ciphertext
        """
        return self.cipher.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypts data using the RSA key
        
        Args:
            data (bytes): ciphertext to decrypt
        
        Returns:
            bytes: decrypted plaintext
        """
        return self.cipher.decrypt(data)

class CryptoHelperAES:
    """
    AES encryption and decryption helper

    Args:
        key (bytes, optional): AES key; if not provided, will generate random key
    """

    def __init__(self, key:bytes=None):
        if key == None:
            self.key = self.generateKey()
        else:
            self.key = key

    def encrypt(self, data:bytes) -> bytes:
        """
        Encrypts data using the AES cipher (in EAX mode).
        
        Args:
            data (bytes): Plaintext data to encrypt
        
        Returns:
            bytes: Nonce (16 bytes) + tag (16 bytes) + ciphertext
        """ 
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        encrypted, tag = cipher.encrypt_and_digest(data)
        return nonce + tag + encrypted

    def decrypt(self, data:bytes) -> bytes:
        """
        Decrypts data encrypted with AES-EAX and verifies its integrity
        
        Args:
            data (bytes): Concatenated nonce, tag, and ciphertext.
        
        Returns:
            bytes: Decrypted plaintext.
        
        Raises:
            DecryptionError: If data authentication fails.
        """
        nonce = data[:16]
        tag = data[16:32]
        ciphertext = data[32:]

        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        decrypted = cipher.decrypt(ciphertext)
        try:
            cipher.verify(tag)
            return decrypted
        except ValueError:
            raise DecryptionError("Message verification failed.")

    def generateKey(self):
        """
        Generates a new random AES key.

        Returns:
            bytes: Randomly generated 32 bytes (AES key)
        """
        return Random.get_random_bytes(32)
