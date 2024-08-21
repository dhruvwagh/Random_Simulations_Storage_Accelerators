from __future__ import with_statement
import os
import sys
import errno
from fuse import FUSE, FuseOSError, Operations

class VirtualStorage(Operations):
    def __init__(self):
        self.data = {}

    def getattr(self, path, fh=None):
        if path == '/':
            return dict(st_mode=(0o755 | 0o040000), st_nlink=2)
        elif path in self.data:
            return dict(st_mode=(0o644 | 0o100000), st_nlink=1,
                        st_size=len(self.data[path]))
        raise FuseOSError(errno.ENOENT)

    def read(self, path, size, offset, fh):
        return self.data[path][offset:offset + size]

    def write(self, path, data, offset, fh):
        if path not in self.data:
            self.data[path] = b''
        self.data[path] = self.data[path][:offset] + data + self.data[path][offset + len(data):]
        return len(data)

    def create(self, path, mode):
        self.data[path] = b''
        return 0

    def unlink(self, path):
        self.data.pop(path)

    def truncate(self, path, length, fh=None):
        self.data[path] = self.data[path][:length]
        return 0

    def flush(self, path, fh):
        return 0

    def release(self, path, fh):
        return 0

    def fsync(self, path, datasync, fh):
        return 0

    def readdir(self, path, fh):
        return ['.', '..'] + [os.path.basename(x) for x in self.data.keys()]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s <mountpoint>' % sys.argv[0])
        sys.exit(1)

    fuse = FUSE(VirtualStorage(), sys.argv[1], foreground=True, nonempty=True)