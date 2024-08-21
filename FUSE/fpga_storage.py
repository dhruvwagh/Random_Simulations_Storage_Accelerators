import os
import errno
from fuse import FuseOSError, Operations
import hashlib

class FPGAStorageHandler(Operations):
    def __init__(self, num_drives, drive_capacity):
        self.drives = [{'capacity': drive_capacity, 'data': {}} for _ in range(num_drives)]
        self.num_drives = num_drives

    def hash_path(self, path):
        return int(hashlib.md5(path.encode()).hexdigest(), 16) % self.num_drives

    def create(self, path, mode):
        drive_index = self.hash_path(path)
        self.drives[drive_index]['data'][path] = b''
        return 0

    def read(self, path, size, offset, fh):
        drive_index = self.hash_path(path)
        return self.drives[drive_index]['data'][path][offset:offset+size]

    def write(self, path, data, offset, fh):
        drive_index = self.hash_path(path)
        file_data = bytearray(self.drives[drive_index]['data'].get(path, b''))
        file_data[offset:offset+len(data)] = data
        self.drives[drive_index]['data'][path] = bytes(file_data)
        return len(data)

    def truncate(self, path, length, fh=None):
        drive_index = self.hash_path(path)
        self.drives[drive_index]['data'][path] = self.drives[drive_index]['data'].get(path, b'')[:length]

    def getattr(self, path, fh=None):
        if path == '/':
            return dict(st_mode=(os.S_IFDIR | 0o755), st_nlink=2)
        drive_index = self.hash_path(path)
        if path in self.drives[drive_index]['data']:
            return dict(st_mode=(os.S_IFREG | 0o644), st_nlink=1,
                        st_size=len(self.drives[drive_index]['data'][path]))
        raise FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        return ['.', '..'] + [os.path.basename(f) for drive in self.drives for f in drive['data']]