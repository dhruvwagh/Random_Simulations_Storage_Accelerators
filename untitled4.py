#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 22:23:29 2023

@author: dhruv
"""

import random
import string
import hashlib
import matplotlib.pyplot as plt
import time

start_time= time.time()

# Function to generate a random string of given length
def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

class SeqBuff:
    def __init__(self):
        self.entries = []

    def append(self, hashed_key, value):
        self.entries.append((hashed_key, value))

    def search(self, hashed_key):
        for index, entry in enumerate(reversed(self.entries)):
            if entry[0] == hashed_key:
                return entry[1], len(self.entries) - index - 1  # Return value and index from end
        return None, None

# Global Welcome_Buff dictionary with large size (100000 entries)
Welcome_Buff = {}

# Generating random key-value insertions in Welcome_Buff
num_insertions_welcome = 100000  # Number of insertions in Welcome_Buff
key_length = 10  # Length of the keys
value_length = 20  # Length of the values

for index in range(num_insertions_welcome):
    key = generate_random_string(key_length)
    value = generate_random_string(value_length)
    hashed_key = hashlib.sha256(key.encode()).hexdigest()  # Hash the key
    Welcome_Buff[key] = value  # Adding to the Welcome_Buff with original key

# Number of pairs of hash_buffs and seq_buffs
num_pairs = 10

# Creating lists to store pairs of hash_buffs and seq_buffs
hash_buffs_list = []
seq_buffs_list = []

# Transfer data from Welcome_Buff to SeqBuff and Hash_Buff for each pair
for _ in range(num_pairs):
    seq_buff = SeqBuff()
    hash_buff = {}
    for key, value in Welcome_Buff.items():
        hashed_key = hashlib.sha256(key.encode()).hexdigest()  # Hash the key
        seq_buff.append(hashed_key, value)  # Adding to the SeqBuff with hashed key
        prefix = hashed_key[:6]
        if prefix in hash_buff:
            hash_buff[prefix].append((hashed_key, seq_buff.search(hashed_key)[1]))  # Append (hashed_key, index)
        else:
            hash_buff[prefix] = [(hashed_key, seq_buff.search(hashed_key)[1])]  # Create new entry with (hashed_key, index)
        if len(hash_buff[prefix]) >= 2000:  # If hash_buff for this prefix is filled, move to the next pair
            break
    hash_buffs_list.append(hash_buff)
    seq_buffs_list.append(seq_buff)

# Bucket sort based on the first 6 bits of the hashed keys for each pair
sorted_buff = []
for hash_buff, seq_buff in zip(hash_buffs_list, seq_buffs_list):
    for prefix in sorted(hash_buff.keys()):
        for hashed_key, index in hash_buff[prefix]:
            sorted_buff.append((hashed_key, seq_buff.entries[index][1]))  # Append (hashed_key, value)

# Print the first few entries in sorted_buff for demonstration
print("Sorted Entries in sorted_buff:")
for entry in sorted_buff[:10]:
    print(entry)

sorted_buff = []
buckets = [0] * 64  # Initialize a list to store the number of elements in each bucket

for hash_buff, seq_buff in zip(hash_buffs_list, seq_buffs_list):
    for prefix in sorted(hash_buff.keys()):
        for hashed_key, index in hash_buff[prefix]:
            sorted_buff.append((hashed_key, seq_buff.entries[index][1]))  # Append (hashed_key, value)
            bucket_index = int(hashed_key, 16) % 64  # Convert the first 6 bits of hashed_key to an integer between 0 and 63
            buckets[bucket_index] += 1  # Increment the count of elements in the corresponding bucket

# Print the number of elements in each bucket for demonstration
print("Number of Elements in Each Bucket:")
for i, count in enumerate(buckets):
    print(f"Bucket {i}: {count} elements")

end_time = time.time()
time_taken = end_time - start_time

# Calculate the throughput (key-value pairs per second)
total_key_value_pairs = num_insertions_welcome
throughput = total_key_value_pairs / time_taken

# Print the throughput
print(f"Throughput: {throughput:.2f} key-value pairs per second")

# Plotting the number of elements in each bucket
plt.bar(range(64), buckets)
plt.xlabel("Bucket Index")
plt.ylabel("Number of Elements")
plt.title("Number of Elements in Each Bucket")
plt.show()

bucket_sizes = {}
for count in buckets:
    if count in bucket_sizes:
        bucket_sizes[count] += 1
    else:
        bucket_sizes[count] = 1

# Rearrange the buckets based on their sizes (sort by the number of elements in the bucket)
sorted_bucket_sizes = sorted(bucket_sizes.items(), key=lambda x: x[0])

# Get the sizes and counts of the buckets after rearranging
sorted_sizes = [size for size, count in sorted_bucket_sizes]
sorted_counts = [count for size, count in sorted_bucket_sizes]

# Plot the bar chart of the number of buckets based on their sizes
plt.bar(sorted_sizes, sorted_counts)
plt.xlabel("Bucket Size")
plt.ylabel("Number of Buckets")
plt.title("Number of Buckets Based on Their Sizes")
plt.show()