import threading
import queue
import hashlib
import random
import time
import statistics

class SimulatedDrive:
    def __init__(self, capacity, io_speed):
        self.capacity = capacity
        self.blocks = {}
        self.io_speed = io_speed  # MB/s
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.operations_count = 0
        self.total_latency = 0
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _process_queue(self):
        while True:
            op, block_num, data, result = self.queue.get()
            start_time = time.time()
            time.sleep(4096 / (self.io_speed * 1024 * 1024))  # Simulate I/O time
            if op == 'read':
                result.put(self.blocks.get(block_num, b'\x00' * 4096))
            elif op == 'write':
                with self.lock:
                    self.blocks[block_num] = data
            end_time = time.time()
            self.operations_count += 1
            self.total_latency += (end_time - start_time)
            self.queue.task_done()

    def read_block(self, block_num):
        result = queue.Queue()
        self.queue.put(('read', block_num, None, result))
        return result.get()

    def write_block(self, block_num, data):
        if block_num >= self.capacity:
            raise IOError("Block number exceeds drive capacity")
        result = queue.Queue()
        self.queue.put(('write', block_num, data, result))
        self.queue.join()

    def get_stats(self):
        if self.operations_count == 0:
            return 0
        return self.total_latency / self.operations_count

class SimulatedMultiDriveSystem:
    def __init__(self, num_drives, drive_capacity, io_speeds):
        self.drives = [SimulatedDrive(drive_capacity, io_speeds[i]) for i in range(num_drives)]
        self.num_drives = num_drives

    def read_block(self, global_block_num):
        drive_index = global_block_num % self.num_drives
        local_block_num = global_block_num // self.num_drives
        return self.drives[drive_index].read_block(local_block_num)

    def write_block(self, global_block_num, data):
        drive_index = global_block_num % self.num_drives
        local_block_num = global_block_num // self.num_drives
        self.drives[drive_index].write_block(local_block_num, data)

    def get_drive_stats(self):
        return [drive.get_stats() for drive in self.drives]

class StorageHandler:
    def __init__(self, num_drives, drive_capacity, io_speeds):
        self.drive_system = SimulatedMultiDriveSystem(num_drives, drive_capacity, io_speeds)
        self.metadata = {}
        self.next_block = 1

    def hash_path(self, path):
        return hashlib.md5(path.encode()).hexdigest()[:8]

    def allocate_blocks(self, num_blocks):
        start_block = self.next_block
        self.next_block += num_blocks
        return start_block

    def create_file(self, path, size):
        if path in self.metadata:
            raise IOError("File already exists")
        
        num_blocks = (size + 4095) // 4096
        start_block = self.allocate_blocks(num_blocks)
        
        self.metadata[path] = {
            'start_block': start_block,
            'size': size
        }

    def read_file(self, path, offset, size):
        if path not in self.metadata:
            raise IOError("File not found")
        
        metadata = self.metadata[path]
        start_block = metadata['start_block'] + (offset // 4096)
        end_block = start_block + ((offset + size - 1) // 4096)
        
        data = b''
        for block in range(start_block, end_block + 1):
            data += self.drive_system.read_block(block)

        start_offset = offset % 4096
        return data[start_offset:start_offset+size]

    def write_file(self, path, offset, data):
        if path not in self.metadata:
            raise IOError("File not found")
        
        metadata = self.metadata[path]
        start_block = metadata['start_block'] + (offset // 4096)
        
        for i in range(0, len(data), 4096):
            block_data = data[i:i+4096]
            self.drive_system.write_block(start_block + (i // 4096), block_data)

        new_size = max(metadata['size'], offset + len(data))
        metadata['size'] = new_size

    def get_stats(self):
        return self.drive_system.get_drive_stats()