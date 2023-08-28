import queue
import threading
import time

# Create thread-safe queues for original key-value pairs and buckets
original_data_queue = queue.Queue()
buckets = [queue.Queue() for _ in range(8)]  # 8 buckets for 3 MSBs

# Function to generate a hash key for a given key
def generate_hash_key(key):
    return hash(key) % (2**64)

# Function to calculate the bucket index for a given hash key
def get_bucket_index(hash_key):
    msbs = (hash_key >> 32) & 0b111  # Extract 3 MSBs
    return msbs

# Function to take key-value pairs from the original queue,
# extract the hash key, and put them in the appropriate bucket queue
def bucket_sort():
    while True:
        try:
            key, value = original_data_queue.get_nowait()  # Wait for up to 1 second
            hash_key = generate_hash_key(key)
            msbs = get_bucket_index(hash_key)
            print(f"Received (Bucket {msbs}): Hash Key: {hash_key}, Value: {value}")
            buckets[msbs].put((hash_key, value))
            original_data_queue.task_done()  # Mark the task as done
        except queue.Empty:
            pass  # No data in the original queue, continue processing or do other tasks

# New function to read data from a specific logical block address
def read_logical_block(logical_block_address):
    while True:
        try:
            key, value = original_data_queue.get_nowait()
            if key == logical_block_address:
                print(f"Logical Block Address: {logical_block_address}")
                print(f"Corresponding Value: {value}")
                original_data_queue.put((key, value))  # Put the item back in the queue
                break
            else:
                original_data_queue.put((key, value))  # Put the item back in the queue
        except queue.Empty:
            print("No data found for the provided logical block address.")
            break

# New loop for user input
def main_loop():
    input_thread = threading.Thread(target=bucket_sort, daemon=True)
    input_thread.start()
    
    while True:
        user_input = input("Enter 'read' or 'write' followed by a logical block address and value (if writing): ")
        parts = user_input.split()

        if len(parts) >= 2:
            command = parts[0]
            logical_block_address = int(parts[1])

            if command == 'read':
                read_logical_block(logical_block_address)
            elif command == 'write' and len(parts) >= 3:
                value = ' '.join(parts[2:])
                original_data_queue.put((logical_block_address, value))
                print(f"Writing to Original Data Queue: Logical Block Address: {logical_block_address}, Value: {value}")
            else:
                print("Invalid command format. Usage: 'read <logical_block_address>' or 'write <logical_block_address> <value>'")
        else:
            print("Invalid command format. Usage: 'read <logical_block_address>' or 'write <logical_block_address> <value>'")

if __name__ == "__main__":
    main_loop()