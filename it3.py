import random
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

# ... (same as before) ...

def count_buckets_elements():
    bucket_counts = [len(bucket) for bucket in hash_buff]
    return bucket_counts

def display_buckets_elements():
    bucket_counts = count_buckets_elements()
    if not any(bucket_counts):
        print("No elements in the hash buckets.")
    else:
        print("Number of Elements in Each Hash Bucket:")
        for i, count in enumerate(bucket_counts, start=1):
            print(f"Bucket {i}: {count} elements")

    # Plot bar chart for number of elements in each hash bucket
    plt.bar(range(1, len(bucket_counts) + 1), bucket_counts)
    plt.xlabel("Bucket")
    plt.ylabel("Number of Elements")
    plt.title("Number of Elements in Each Hash Bucket")
    plt.show()

    # Plot bar chart for number of buckets with a certain number of elements
    unique_counts, counts = zip(*sorted(zip(*np.unique(bucket_counts, return_counts=True))))
    plt.bar(unique_counts, counts)
    plt.xlabel("Number of Elements")
    plt.ylabel("Number of Buckets")
    plt.title("Number of Buckets with a Certain Number of Elements")
    plt.show()



# Constants
WELCOME_BUFF_CAPACITY = 100000

SEQ_BUFF_CAPACITY = 1000
HASH_BUFF_CAPACITY = 1000
SORTED_BUFF_CAPACITY = 1000
TOTAL_KEY_VALUE_PAIRS = 100000

# Global variables
welcome_buff = []
seq_buff = []
hash_buff = []
sorted_buff = []
global_index = {}
local_indices = [{} for _ in range(HASH_BUFF_CAPACITY)]

import random
import pandas as pd

# ... (same as before) ...

def display_indices():
    global global_index, local_indices

    # Display Global Index
    global_df = pd.DataFrame(list(global_index.items()), columns=["Hashed Key", "Block Cluster ID"])
    if global_df.empty:
        print("Global Index: Empty")
    else:
        print("Global Index:")
        print(global_df.to_string(index=False))

    # Display Local Indices
    if not any(local_indices):
        print("Local Indices: Empty")
    else:
        print("Local Indices:")
        for i, local_index in enumerate(local_indices, start=1):
            if not local_index:
                continue
            local_df = pd.DataFrame(list(local_index.items()), columns=["Hashed Key", "Entry Location"])
            print(f"\nBlock Cluster {i}:")
            print(local_df.to_string(index=False))

# ... (same as before) ...


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
            # Update global index
            global_index[hashed_key] = len(sorted_buff)
            # Update local index
            local_indices[hashed_key][hashed_key] = len(seq_buff) - 1

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
    for i, block_cluster in enumerate(sorted_buff, start=1):
        print(f"Block Cluster {i}: {block_cluster}")

def display_indices():
    global global_index, local_indices
    global_df = pd.DataFrame(list(global_index.items()), columns=["Hashed Key", "Block Cluster ID"])
    local_dfs = []
    for i, local_index in enumerate(local_indices):
        if local_index:
            local_df = pd.DataFrame(list(local_index.items()), columns=["Hashed Key", "Entry Location"])
            local_dfs.append(local_df)
    if global_df.empty:
        print("Global Index: Empty")
    else:
        print("Global Index:")
        print(global_df)
    if not local_dfs:
        print("Local Indices: Empty")
    else:
        print("Local Indices:")
        for i, local_df in enumerate(local_dfs, start=1):
            print(f"Block Cluster {i}:")
            print(local_df)

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

    # Display the indices
    display_indices()
    display_indices()

    # Display the number of elements in each hash bucket
    display_buckets_elements()
