import queue
import threading
import time

# Create thread-safe queues for original key-value pairs and buckets
original_data_queue = queue.Queue()
buckets = [queue.Queue() for _ in range(8)]  # 8 buckets for 3 MSBs

# Define the value block size in bytes
VALUE_BLOCK_SIZE = 4 * 1024  # 4KB

# Function to generate a hash key for a given key
def generate_hash_key(key):
    return hash(key) % (2**64)

# Function to continuously read user input and append values to the original queue
def input_reader():
    while True:
        try:
            key = int(input("Enter a key (integer): "))
            if key < 0 or key >= 2**64:
                print("Key must be a non-negative integer less than 2^64.")
                continue
            
            value = input("Enter a value (up to 4KB): ")
            value_size = len(value.encode())  # Size in bytes
            if value_size > VALUE_BLOCK_SIZE:
                print("Value size cannot exceed 4KB.")
                continue
            
            original_data_queue.put((key, value))
            time.sleep(1)  # Just to avoid overwhelming the console
        
        except ValueError:
            print("Invalid input. Key must be a non-negative integer.")

# Function to take key-value pairs from the original queue,
# extract the hash key, and put them in the appropriate bucket queue
def bucket_sort():
    while True:
        try:
            key, value = original_data_queue.get(timeout=1)  # Wait for up to 1 second
            hash_key = generate_hash_key(key)
            msbs = (hash_key >> 61) & 0b111  # Extract 3 MSBs
            buckets[msbs].put((hash_key, value))
            original_data_queue.task_done()  # Mark the task as done
        except queue.Empty:
            pass  # No data in the original queue, continue processing or do other tasks

# Start the input_reader and bucket_sort threads
input_thread = threading.Thread(target=input_reader, daemon=True)
input_thread.start()

bucket_sort_thread = threading.Thread(target=bucket_sort, daemon=True)
bucket_sort_thread.start()

# Main loop to process data from the buckets
while True:
    for i in range(8):
        try:
            hash_key, value = buckets[i].get_nowait()
            print(f"Received (Bucket {i}): Hash Key: {hash_key}, Value: {value}")
            buckets[i].task_done()
        except queue.Empty:
            pass  # No data in the bucket queue, continue processing or do other tasks
