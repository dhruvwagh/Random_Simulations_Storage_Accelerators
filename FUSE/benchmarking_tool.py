import subprocess
import os
import time
import matplotlib.pyplot as plt

# Configuration
MOUNT_POINT = "/mnt/virtualdrive"
FUSE_SCRIPT_PATH = "/home/parallels/Documents/Random_Simulations_Storage_Accelerators/FUSE/storage_accelerator.py"  # Update with the actual path to your FUSE script
NUM_DRIVES = 3
FIO_OUTPUT_FILE = "fio_results.txt"

def mount_fuse():
    # Mount the FUSE filesystem
    print("Mounting FUSE-based storage system...")
    mount_cmd = f"python3 {FUSE_SCRIPT_PATH} {MOUNT_POINT} {NUM_DRIVES}"
    subprocess.Popen(mount_cmd, shell=True)
    time.sleep(3)  # Wait a bit for the mount to complete

def unmount_fuse():
    # Unmount the FUSE filesystem
    print("Unmounting FUSE-based storage system...")
    unmount_cmd = f"fusermount -u {MOUNT_POINT}"
    subprocess.run(unmount_cmd, shell=True)

def run_fio_test():
    # Run FIO benchmark
    print("Running FIO benchmark...")
    fio_cmd = f"fio --name=benchmark --directory={MOUNT_POINT} --size=1G --bs=4k --rw=randrw " \
              f"--ioengine=sync --iodepth=32 --runtime=60 --time_based --group_reporting --output={FIO_OUTPUT_FILE}"
    subprocess.run(fio_cmd, shell=True)

def parse_fio_results():
    # Parse the FIO results to extract relevant data
    iops = []
    latency = []
    
    with open(FIO_OUTPUT_FILE, 'r') as file:
        for line in file:
            if "iops=" in line:
                iops.append(float(line.split("iops=")[1].split(",")[0]))
            if "clat" in line and "avg=" in line:
                latency.append(float(line.split("avg=")[1].split(",")[0].replace("us", "")))

    return iops, latency

def plot_results(iops, latency):
    # Plot the IOPS and latency results
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.plot(iops, 'o-')
    plt.title("IOPS over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("IOPS")

    plt.subplot(1, 2, 2)
    plt.plot(latency, 'o-')
    plt.title("Latency over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Latency (us)")

    plt.tight_layout()
    plt.savefig("benchmark_results.png")
    plt.show()

def main():
    mount_fuse()
    
    try:
        run_fio_test()
    finally:
        unmount_fuse()

    iops, latency = parse_fio_results()
    plot_results(iops, latency)

if __name__ == "__main__":
    main()
