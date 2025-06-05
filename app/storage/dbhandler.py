from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

class DBFailure(Exception):
    """
    Raised when the database handler fails to initialize or connect to MongoDB.
    """
    pass

class DBHandler:
    """
    Handles database operations related to client authentication using MongoDB.

    Provides access to client secrets for verifying client identity during the authentication handshake.
    """
    def __init__(self, db_address:str, db_user:str, db_password:str, db_name:str):
        """
        Initializes a connection to the MongoDB database and prepares the clients collection.

        Args:
            db_address (str): Address of the MongoDB server (e.g. 'localhost:27017').
            db_user (str): Username for authenticating with the database.
            db_password (str): Password for authenticating with the database.
            db_name (str): Name of the MongoDB database to use.

        Raises:
            DBFailure: If the connection to MongoDB fails.
        """
        try:
            self.client = MongoClient(f'mongodb://{db_user}:{db_password}@{db_address}')
            self.db = self.client[db_name]
            self.secretsCollection = self.db['clients']
        except Exception as e:
            logging.critical(f"Failed to initialize DBHandler: {e}")
            raise DBFailure

    def getSharedSecret(self, clientId: str) -> bytes | None:
        """
        Retrieves the shared secret associated with a given client ID.

        Args:
            clientId (str): The client's ID. 
        Returns:
            bytes or None: The shared secret as a byte string if found, otherwise None.
        """
        entry = self.secretsCollection.find_one({"client_id": clientId})
        if entry:
            return entry.get("secret")
        return None

