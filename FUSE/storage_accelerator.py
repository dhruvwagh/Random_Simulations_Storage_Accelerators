import os
import sys
import threading
import hashlib
import queue
import time
from fuse import FUSE, Operations

class SimulatedDrive:
    def __init__(self):
        self.files = {}
        self.lock = threading.Lock()
        self.queue = queue.Queue()
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _process_queue(self):
        while True:
            operation, args = self.queue.get()
            if operation == "read":
                result = self._read_file(*args)
            elif operation == "write":
                result = self._write_file(*args)
            # Simulate some drive latency
            time.sleep(0.01)
            self.queue.task_done()
            if result is not None:
                args[-1].set(result)

    def create_file(self, path, content=b""):
        with self.lock:
            self.files[path] = content

    def _read_file(self, path, size, offset):
        with self.lock:
            if path in self.files:
                return self.files[path][offset:offset + size]
            else:
                raise FileNotFoundError

    def read_file(self, path, size, offset, result_future):
        self.queue.put(("read", (path, size, offset, result_future)))

    def _write_file(self, path, data, offset):
        with self.lock:
            if path not in self.files:
                self.files[path] = b""
            self.files[path] = self.files[path][:offset] + data + self.files[path][offset + len(data):]

    def write_file(self, path, data, offset, result_future):
        self.queue.put(("write", (path, data, offset, result_future)))

    def delete_file(self, path):
        with self.lock:
            if path in self.files:
                del self.files[path]

    def truncate_file(self, path, length):
        with self.lock:
            if path in self.files:
                self.files[path] = self.files[path][:length]

    def list_dir(self, path):
        with self.lock:
            return [p for p in self.files.keys() if p.startswith(path)]

class StorageAccelerator(Operations):
    def __init__(self, num_drives):
        self.drives = [SimulatedDrive() for _ in range(num_drives)]
        self.cache = {}

    def _hash_path(self, path):
        return hashlib.md5(path.encode()).hexdigest()

    def _select_drive(self, path):
        hashed = int(self._hash_path(path), 16)
        return self.drives[hashed % len(self.drives)]

    def getattr(self, path, fh=None):
        return {
            'st_atime': 0, 'st_ctime': 0, 'st_gid': 0,
            'st_mode': 0o100644, 'st_mtime': 0, 'st_nlink': 1,
            'st_size': len(self._select_drive(path).files.get(path, b"")),
            'st_uid': 0
        }

    def readdir(self, path, fh):
        dirents = ['.', '..']
        for drive in self.drives:
            dirents.extend(drive.list_dir(path))
        return set(dirents)

    def read(self, path, size, offset, fh):
        drive = self._select_drive(path)
        result_future = queue.Queue()
        drive.read_file(path, size, offset, result_future)
        return result_future.get()

    def write(self, path, data, offset, fh):
        drive = self._select_drive(path)
        result_future = queue.Queue()
        drive.write_file(path, data, offset, result_future)
        return len(data)

    def create(self, path, mode):
        drive = self._select_drive(path)
        drive.create_file(path)
        return 0

    def truncate(self, path, length, fh=None):
        drive = self._select_drive(path)
        drive.truncate_file(path, length)

    def unlink(self, path):
        drive = self._select_drive(path)
        drive.delete_file(path)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s <mountpoint> <num_drives>' % sys.argv[0])
        sys.exit(1)

    mountpoint = sys.argv[1]
    num_drives = int(sys.argv[2])
    
    FUSE(StorageAccelerator(num_drives), mountpoint, nothreads=True, foreground=True)
