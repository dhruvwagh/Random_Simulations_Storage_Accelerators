import os
import errno
from fuse import FUSE, FuseOSError, Operations
import random

class OSStorageHandler:
    def __init__(self, num_drives, drive_capacity):
        self.drives = [{'capacity': drive_capacity, 'data': {}} for _ in range(num_drives)]
        self.num_drives = num_drives

    def create_file(self, path, size):
        drive_index = random.randint(0, self.num_drives - 1)
        self.drives[drive_index]['data'][path] = b'\x00' * size

    def read_file(self, path, offset, size):
        for drive in self.drives:
            if path in drive['data']:
                return drive['data'][path][offset:offset+size]
        raise IOError("File not found")

    def write_file(self, path, offset, data):
        for drive in self.drives:
            if path in drive['data']:
                file_data = bytearray(drive['data'][path])
                file_data[offset:offset+len(data)] = data
                drive['data'][path] = bytes(file_data)
                return
        raise IOError("File not found")

    def get_files(self):
        files = []
        for drive in self.drives:
            files.extend(drive['data'].keys())
        return files

class OSFuse(Operations):
    def __init__(self, num_drives, drive_capacity):
        self.storage = OSStorageHandler(num_drives, drive_capacity)

    def create(self, path, mode):
        self.storage.create_file(path, 0)
        return 0

    def read(self, path, size, offset, fh):
        return self.storage.read_file(path, offset, size)

    def write(self, path, data, offset, fh):
        self.storage.write_file(path, offset, data)
        return len(data)

    def truncate(self, path, length, fh=None):
        self.storage.create_file(path, length)
        return 0

    def getattr(self, path, fh=None):
        if path == '/':
            return dict(st_mode=(os.S_IFDIR | 0o755), st_nlink=2)
        try:
            data = self.storage.read_file(path, 0, 1)
            return dict(st_mode=(os.S_IFREG | 0o644), st_nlink=1,
                        st_size=len(data))
        except:
            raise FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        return ['.', '..'] + [os.path.basename(f) for f in self.storage.get_files()]