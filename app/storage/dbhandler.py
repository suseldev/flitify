from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

class DBFailure(Exception):
    pass

class DBHandler:
    def __init__(self, db_address:str, db_user:str, db_password:str, db_name:str):
        try:
            self.client = MongoClient(f'mongodb://{db_user}:{db_password}@{db_address}')
            self.db = self.client[db_name]
            self.secretsCollection = self.db['clients']
        except Exception as e:
            logging.critical(f"Failed to initialize DBHandler: {e}")
            raise DBFailure

    def getSharedSecret(self, clientId: str) -> bytes | None:
        entry = self.secretsCollection.find_one({"client_id": clientId})
        if entry:
            return entry.get("secret")
        return None

