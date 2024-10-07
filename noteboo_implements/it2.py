import random

# Constants
WELCOME_BUFF_CAPACITY = 100
SEQ_BUFF_CAPACITY = 1000
HASH_BUFF_CAPACITY = 1000
SORTED_BUFF_CAPACITY = 1000
TOTAL_KEY_VALUE_PAIRS = 100000

# Global variables
welcome_buff = []
seq_buff = []
hash_buff = []
sorted_buff = []

# Helper functions
def generate_random_key_value_pairs(num_pairs):
    return [(f"Key{i}", f"Value{i}") for i in range(num_pairs)]

def hash_key(key):
    # Placeholder hash function (for simplicity)
    return hash(key) % HASH_BUFF_CAPACITY

def move_to_seq_buff(key_value_pairs):
    for key, value in key_value_pairs:
        hashed_key = hash_key(key)
        if (key, value) in welcome_buff:
            welcome_buff.remove((key, value))
            seq_buff.append((hashed_key, value))

def bucket_sort():
    global hash_buff
    buckets = [[] for _ in range(HASH_BUFF_CAPACITY)]
    for hashed_key, value in seq_buff:
        buckets[hashed_key].append((hashed_key, value))
    hash_buff = [bucket for bucket in buckets if bucket]

def create_block_cluster():
    global sorted_buff
    block_cluster = []
    for bucket in hash_buff:
        for _, value in bucket:
            block_cluster.append(value)
    sorted_buff.append(block_cluster)

def flush_to_storage():
    global sorted_buff
    for block_cluster in sorted_buff:
        print("Flushing to storage:", block_cluster)

# Simulation
if __name__ == "__main__":
    # Generate random key-value pairs
    key_value_pairs = generate_random_key_value_pairs(TOTAL_KEY_VALUE_PAIRS)

    # Populate the Welcome-Buff
    welcome_buff = key_value_pairs[:WELCOME_BUFF_CAPACITY]

    # Process key-value pairs in batches
    for i in range(0, TOTAL_KEY_VALUE_PAIRS, SEQ_BUFF_CAPACITY):
        batch = key_value_pairs[i:i+SEQ_BUFF_CAPACITY]

        # Move to Seq-Buff and Hash-Buff
        move_to_seq_buff(batch)

        # Bucket-sort and create Block Clusters
        bucket_sort()
        create_block_cluster()

        # Flush to storage
        flush_to_storage()

    # Final state
    print("Final state of Sorted-Buff:")
    for block_cluster in sorted_buff:
        print(block_cluster)
