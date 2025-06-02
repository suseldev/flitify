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
        # TODO: Dummy data
        return {
            'uptime_seconds': 36812,
            'current_user': 'jakub',
            'cpu_usage': 34,
            'memory_total': 8.00,
            'memory_used': 3.62,
            'disks': {
                '/dev/sda1': {
                    'used': 83.97,
                    'total': 512
                    }
                },
            'running_applications': {
                    'chrome.exe': {'name': 'Google Chrome', 'open_windows': 2},
                    'Codeblocks': {'name': 'CodeBlocks', 'open_windows': 1}
                }
        }
