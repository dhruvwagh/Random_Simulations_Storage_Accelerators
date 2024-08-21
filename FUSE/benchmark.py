import os
import time
import random
import subprocess
import matplotlib.pyplot as plt
from fuse import FUSE
from fpga_storage import FPGAStorageHandler
from xdp_storage import XDPStorageHandler
from os_storage import OSStorageHandler

def mount_filesystem(StorageClass, mount_point, num_drives, drive_capacity):
    FUSE(StorageClass(num_drives, drive_capacity), mount_point, nothreads=True, foreground=False)

def unmount_filesystem(mount_point):
    subprocess.run(['fusermount', '-u', mount_point])

def run_benchmark(mount_point, num_files, file_size, num_reads, num_writes):
    # Create files
    start_time = time.time()
    for i in range(num_files):
        with open(os.path.join(mount_point, f'file{i}.txt'), 'w') as f:
            f.write('0' * file_size)
    create_time = time.time() - start_time

    # Read files
    start_time = time.time()
    for _ in range(num_reads):
        i = random.randint(0, num_files - 1)
        with open(os.path.join(mount_point, f'file{i}.txt'), 'r') as f:
            f.read()
    read_time = time.time() - start_time

    # Write to files
    start_time = time.time()
    for _ in range(num_writes):
        i = random.randint(0, num_files - 1)
        with open(os.path.join(mount_point, f'file{i}.txt'), 'w') as f:
            f.write('1' * file_size)
    write_time = time.time() - start_time

    return {
        'create_time': create_time,
        'read_time': read_time,
        'write_time': write_time
    }

def plot_results(results):
    systems = list(results.keys())
    create_times = [results[system]['create_time'] for system in systems]
    read_times = [results[system]['read_time'] for system in systems]
    write_times = [results[system]['write_time'] for system in systems]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

    ax1.bar(systems, create_times)
    ax1.set_ylabel('Create Time (s)')
    ax1.set_title('File Creation Time Comparison')

    ax2.bar(systems, read_times)
    ax2.set_ylabel('Read Time (s)')
    ax2.set_title('File Read Time Comparison')

    ax3.bar(systems, write_times)
    ax3.set_ylabel('Write Time (s)')
    ax3.set_title('File Write Time Comparison')

    plt.tight_layout()
    plt.savefig('benchmark_results.png')
    plt.close()

if __name__ == "__main__":
    NUM_DRIVES = 5
    DRIVE_CAPACITY = 1000000  # blocks
    NUM_FILES = 1000
    FILE_SIZE = 1024  # bytes
    NUM_READS = 10000
    NUM_WRITES = 10000

    results = {}
    mount_point = '/tmp/fuse_mount'

    # Remove the mount point if it already exists
    if os.path.exists(mount_point):
        try:
            os.rmdir(mount_point)
        except OSError:
            print(f"Error: {mount_point} exists and is not empty. Please remove it manually.")
            exit(1)

    for StorageClass in [FPGAStorageHandler, XDPStorageHandler, OSStorageHandler]:
        class_name = StorageClass.__name__
        print(f"Running benchmark for {class_name}...")

        os.makedirs(mount_point)
        mount_filesystem(StorageClass, mount_point, NUM_DRIVES, DRIVE_CAPACITY)

        results[class_name] = run_benchmark(mount_point, NUM_FILES, FILE_SIZE, NUM_READS, NUM_WRITES)
        print(f"{class_name} results: {results[class_name]}")

        unmount_filesystem(mount_point)
        os.rmdir(mount_point)

    plot_results(results)
    print("Benchmark complete. Results plotted in 'benchmark_results.png'")