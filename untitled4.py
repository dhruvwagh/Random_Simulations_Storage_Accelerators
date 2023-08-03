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
