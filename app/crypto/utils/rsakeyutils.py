from Crypto.PublicKey import RSA
import os
import sys

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

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <directory to store RSA keys>")
        sys.exit(1)
    dirname = sys.argv[1]
    if os.path.isdir(dirname):
        print("Generating RSA keys...")
        generateRsaKeypair(dirname + '/priv_key.pem', dirname + '/pub_key.pem')
        print("RSA keys generated")
    else:
        print(f"Invalid path: {dirname}")

if __name__ == "__main__":
    main()
