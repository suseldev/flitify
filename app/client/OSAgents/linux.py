import os
from client.OSAgents.osagent import OSAgent

class LinuxAgent(OSAgent):
    def getDirectoryListing(self, path:str) -> list:
        if not os.path.isdir(path):
            raise FileNotFoundError(f'{path} is not a directory')
        entries = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            entries.append({
                'name': entry,
                'type': 'dir' if os.path.isdir(full_path) else 'file'
            })
        return entries

    def getStatus(self):
        pass
