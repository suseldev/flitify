from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
import base64
import os
import hashlib

class DBFailure(Exception):
    pass

class DBHandler:
    def __init__(self, db_address:str, db_user:str, db_password:str, db_name:str):
        try:
            self.client = MongoClient(f'mongodb://{db_user}:{db_password}@{db_address}')
            self.db = self.client[db_name]
            self.secretsCollection = self.db['clients']
            self.usersCollection = self.db['users']
            self.logger = logging.getLogger("backendapiserver")
        except Exception as e:
            self.logger.critical(f"Failed to initialize DBHandler: {e}")
            raise DBFailure

    def getSharedSecret(self, clientId: str) -> bytes | None:
        entry = self.secretsCollection.find_one({"client_id": clientId})
        if entry:
            return entry.get("secret")
        return None

    def createClient(self, clientId: str, secret: str) -> bool:
        if self.secretsCollection.find_one({"client_id": clientId}):
            return False
        self.secretsCollection.insert_one({"client_id": clientId, "secret": secret})
        return True

    def changeClientSecret(self, clientId: str, secret: str) -> bool:
        result = self.secretsCollection.update_one(
            {"client_id": clientId},
            {"$set": {"secret": secret}}
        )
        return result.modified_count > 0

    def deleteClient(self, clientId: str) -> bool:
        result = self.secretsCollection.delete_one({"client_id": clientId})
        return result.deleted_count > 0

    def createUser(self, username: str, password: str) -> bool:
        if self.usersCollection.find_one({"username": username}):
            return False
        salt = os.urandom(16)
        hashed = self._hash_password(password, salt)
        self.usersCollection.insert_one({
            "username": username,
            "password": hashed,
            "salt": base64.b64encode(salt).decode()
        })
        return True

    def loginUser(self, username: str, password: str) -> bool:
        entry = self.usersCollection.find_one({"username": username})
        if not entry or "salt" not in entry:
            return False
        salt = base64.b64decode(entry["salt"])
        hashed_attempt = self._hash_password(password, salt)
        return hashed_attempt == entry.get("password")

    def changeUserPassword(self, username: str, newpassword: str) -> bool:
        salt = os.urandom(16)
        hashed = self._hash_password(newpassword, salt)
        result = self.usersCollection.update_one(
            {"username": username},
            {"$set": {
                "password": hashed,
                "salt": base64.b64encode(salt).decode()
            }}
        )
        return result.modified_count > 0

    def _hash_password(self, password:str, salt:bytes) -> str:
        hashed = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=64)
        return base64.b64encode(hashed).decode()
