class DBHandler():
    def __init__(self, db_address=None, db_password=None, db_table=None):
        # Dummy data for now, will be fetched from db in later stages of development
        self.secrets = {
                'TEST-1': 'abcdefgh',
                'TEST-2': 'qwertyui'
                }

    def getSharedSecret(self, clientId: str) -> bytes | None:
        if clientId not in self.secrets:
            return None
        return self.secrets[clientId]
