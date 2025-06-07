import os
import psutil
import time
import getpass
import string
from client.OSAgents.osagent import OSAgent

class WindowsAgent(OSAgent):
    def getDirectoryListing(self, path:str) -> list:
        path = path.replace('\\', '/')
        if path.strip('/') == '':
            drives = []
            for letter in string.ascii_uppercase:
                drive = f'{letter}:/'
                print(drive)
                if os.path.exists(drive):
                    drives.append({
                        'name': drive,
                        'type': 'dir'
                    })
            return drives
        # return path back to normal
        if path.startswith('/'):
            path = path[1:]
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            print(f'Path "{path}" is not a directory!')
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
        uptime_seconds = time.time() - psutil.boot_time()
        mem = psutil.virtual_memory()
        memory_total_gb = round(mem.total / (1024 ** 3), 2)
        memory_used_gb = round(mem.used / (1024 ** 3), 2)
        cpu_usage = psutil.cpu_percent(interval=1)
        disk_info = {}
        for part in psutil.disk_partitions():
            usage = psutil.disk_usage(part.mountpoint)
            disk_info[part.device] = {
                'used': round(usage.used / (1024 ** 3), 2),
                'total': round(usage.total / (1024 ** 3), 2)
        }
        running_apps = {}
        for proc in psutil.process_iter(['name']):
            try:
                username = proc.username()
                if username and getpass.getuser().lower() in username.lower():
                    name = proc.info['name']
                    if name not in running_apps:
                        running_apps[name] = {'name': name, 'open_windows': 1}
                    else:
                        running_apps[name]['open_windows'] += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            'uptime_seconds': int(uptime_seconds),
            'current_user': getpass.getuser(),
            'cpu_usage': cpu_usage,
            'memory_total': memory_total_gb,
            'memory_used': memory_used_gb,
            'disks': disk_info,
            'running_applications': running_apps
        }
