from Crypto.PublicKey import RSA

def generateRsaKeypair(privKeyTargetPath: str, pubKeyTargetPath: str):
    keyPair = RSA.generate(4096)
    pubKey = keyPair.publickey()
    pubKeyPEM = pubKey.exportKey()
    f = open(pubKeyTargetPath, 'wb')
    f.write(pubKeyPEM)
    f.close()
    privKeyPEM = keyPair.exportKey()
    f = open(privKeyTargetPath, 'wb')
    f.write(privKeyPEM)
    f.close()

def loadKeyFromFile(pubKeyFilePath: str) -> bytes:
    keyF = open(pubKeyFilePath, 'rb')
    key = RSA.importKey(keyF.read())
    keyF.close()
    return key

