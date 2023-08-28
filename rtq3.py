import queue
import threading
import time

# Create thread-safe queues for buckets
buckets = [queue.Queue() for _ in range(8)]  # 8 buckets for 3 MSBs

# Function to calculate the bucket index for a given hash key
def get_bucket_index(hash_key):
    msbs = (hash_key >> 32) & 0b111  # Extract 3 MSBs
    return msbs

# Function to generate a hash key for a given key
def generate_hash_key(key):
    return hash(key) % (2**64)

# New function to read data from a specific logical block address
def read_logical_block(logical_block_address):
    hash_key = generate_hash_key(logical_block_address)
    bucket_index = get_bucket_index(hash_key)
    print(f"Logical Block Address: {logical_block_address}")
    print(f"Calculated Hash Key: {hash_key}")
    print(f"Corresponding Bucket: {bucket_index}")

# New function to write data to a specific logical block address
def write_logical_block(logical_block_address, value):
    hash_key = generate_hash_key(logical_block_address)
    msbs = get_bucket_index(hash_key)
    print(f"Writing (Bucket {msbs}): Hash Key: {hash_key}, Logical Block Address: {logical_block_address}, Value: {value}")
    buckets[msbs].put((hash_key, value))

# New loop for user input
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
            write_logical_block(logical_block_address, value)
        else:
            print("Invalid command format. Usage: 'read <logical_block_address>' or 'write <logical_block_address> <value>'")
    else:
        print("Invalid command format. Usage: 'read <logical_block_address>' or 'write <logical_block_address> <value>'")
