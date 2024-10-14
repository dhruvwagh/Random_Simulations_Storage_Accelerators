import time
import threading

class SimulatedDrive:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}
        self.lock = threading.Lock()

    def read(self, path, size, offset):
        with self.lock:
            time.sleep(0.001)  # Simulate read latency
            return self.data.get(path, b'')[offset:offset + size]

    def write(self, path, data, offset):
        with self.lock:
            time.sleep(0.001)  # Simulate write latency
            file_data = bytearray(self.data.get(path, b''))
            file_data[offset:offset + len(data)] = data
            self.data[path] = bytes(file_data)

    def create(self, path):
        with self.lock:
            self.data[path] = b''

    def truncate(self, path, length):
        with self.lock:
            self.data[path] = self.data.get(path, b'')[:length]

    def getattr(self, path):
        with self.lock:
            if path in self.data:
                return len(self.data[path])
            return None
