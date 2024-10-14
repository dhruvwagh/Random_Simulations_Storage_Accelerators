import time
import os

def benchmark(mountpoint, file_size_mb=100, num_files=10):
    file_size = file_size_mb * 1024 * 1024  # Convert MB to bytes
    results = []

    # Write Benchmark
    start_time = time.time()
    for i in range(num_files):
        with open(f"{mountpoint}/file{i}.dat", "wb") as f:
            f.write(os.urandom(file_size))
    write_duration = time.time() - start_time
    results.append(f"Write: {num_files} files of {file_size_mb}MB each in {write_duration:.2f} seconds")

    # Read Benchmark
    start_time = time.time()
    for i in range(num_files):
        with open(f"{mountpoint}/file{i}.dat", "rb") as f:
            f.read()
    read_duration = time.time() - start_time
    results.append(f"Read: {num_files} files of {file_size_mb}MB each in {read_duration:.2f} seconds")

    # Delete Files
    for i in range(num_files):
        os.remove(f"{mountpoint}/file{i}.dat")

    # Print Results
    for result in results:
        print(result)

if __name__ == "__main__":
    mount_point = "/tmp/fuse_mount"
    # Remove the directory if it exists
    if os.path.exists(mount_point):
        shutil.rmtree(mount_point)
    # Create the directory
    os.makedirs(mount_point)
    
    try:
        mount_fuse()
        run_fio_benchmark()
        benchmark(mount_point)
    finally:
        unmount_fuse()
