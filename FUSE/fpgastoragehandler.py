import os
import errno
from fuse import FUSE, FuseOSError, Operations
import hashlib
import threading

class FPGAStorageHandler(Operations):
    def __init__(self, drives):
        self.drives = drives
        self.num_drives = len(drives)
        self.cache = {}
        self.cache_lock = threading.Lock()

    def hash_path(self, path):
        return int(hashlib.md5(path.encode()).hexdigest(), 16) % self.num_drives

    def read(self, path, size, offset, fh):
        drive_index = self.hash_path(path)
        with self.cache_lock:
            if path in self.cache:
                return self.cache[path][offset:offset + size]

        data = self.drives[drive_index].read(path, size, offset)
        with self.cache_lock:
            self.cache[path] = data
        return data

    def write(self, path, data, offset, fh):
        drive_index = self.hash_path(path)
        self.drives[drive_index].write(path, data, offset)
        with self.cache_lock:
            if path in self.cache:
                file_data = bytearray(self.cache[path])
                file_data[offset:offset + len(data)] = data
                self.cache[path] = bytes(file_data)
        return len(data)

    def create(self, path, mode):
        drive_index = self.hash_path(path)
        self.drives[drive_index].create(path)
        return 0

    def truncate(self, path, length, fh=None):
        drive_index = self.hash_path(path)
        self.drives[drive_index].truncate(path, length)
        return 0

    def getattr(self, path, fh=None):
        if path == '/':
            return dict(st_mode=(os.S_IFDIR | 0o755), st_nlink=2)
        drive_index = self.hash_path(path)
        size = self.drives[drive_index].getattr(path)
        if size is not None:
            return dict(st_mode=(os.S_IFREG | 0o644), st_nlink=1, st_size=size)
        raise FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        return ['.', '..'] + list(set(f for drive in self.drives for f in drive.data))

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('usage: %s <mountpoint> <num_drives>' % sys.argv[0])
        sys.exit(1)

    mountpoint = sys.argv[1]
    num_drives = int(sys.argv[2])
    drive_capacity = 1024 * 1024 * 1024  # 1GB per drive

    drives = [SimulatedDrive(drive_capacity) for _ in range(num_drives)]
    fuse = FUSE(FPGAStorageHandler(drives), mountpoint, foreground=True)
