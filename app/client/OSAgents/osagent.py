import abc

class OSAgent(abc.ABC):
    @abc.abstractmethod
    def getStatus(self):
        pass

    @abc.abstractmethod
    def getDirectoryListing(self, path='/') -> list:
        pass
