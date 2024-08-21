import os
import errno
from fuse import FUSE, FuseOSError, Operations
import hashlib

class XDPStorageHandler:
    def __init__(self, num_drives, drive_capacity):
        self.drives = [{'capacity': drive_capacity, 'data': {}} for _ in range(num_drives)]
        self.buffer = {}
        self.buffer_size = 1000000  # 1GB buffer
        self.num_drives = num_drives

    def hash_function(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % self.num_drives

    def create_file(self, path, size):
        self.buffer[path] = b'\x00' * size
        if sum(len(data) for data in self.buffer.values()) >= self.buffer_size:
            self.flush_buffer()

    def read_file(self, path, offset, size):
        if path in self.buffer:
            return self.buffer[path][offset:offset+size]
        drive_index = self.hash_function(path)
        return self.drives[drive_index]['data'][path][offset:offset+size]

    def write_file(self, path, offset, data):
        if path in self.buffer:
            buffer_data = bytearray(self.buffer[path])
            buffer_data[offset:offset+len(data)] = data
            self.buffer[path] = bytes(buffer_data)
        else:
            drive_index = self.hash_function(path)
            file_data = bytearray(self.drives[drive_index]['data'][path])
            file_data[offset:offset+len(data)] = data
            self.drives[drive_index]['data'][path] = bytes(file_data)

    def flush_buffer(self):
        for path, data in self.buffer.items():
            drive_index = self.hash_function(path)
            self.drives[drive_index]['data'][path] = data
        self.buffer.clear()

    def get_files(self):
        files = list(self.buffer.keys())
        for drive in self.drives:
            files.extend(drive['data'].keys())
        return files

class XDPFuse(Operations):
    def __init__(self, num_drives, drive_capacity):
        self.storage = XDPStorageHandler(num_drives, drive_capacity)

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