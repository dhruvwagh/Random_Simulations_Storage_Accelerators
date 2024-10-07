#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 21:57:58 2023

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

# Creating Welcome_Buff dictionary
Welcome_Buff = {}

# Generating random key-value insertions
num_insertions = 1000000  # Number of insertions
key_length = 10  # Length of the keys
value_length = 20  # Length of the values

# Creating an instance of the SeqBuff class
seq_buff = SeqBuff()

# Additional dictionary to store hashed keys and their indices in SeqBuff
hash_buff = {}

# List to maintain the generated keys for probing
generated_keys_list = []

for index in range(num_insertions):
    key = generate_random_string(key_length)
    generated_keys_list.append(key)  # Maintain the generated keys for probing
    value = generate_random_string(value_length)
    hashed_key = hashlib.sha256(key.encode()).hexdigest()  # Hash the key
    Welcome_Buff[key] = value  # Adding to the Welcome_Buff with original key
    seq_buff.append(hashed_key, value)  # Adding to the SeqBuff with hashed key
    prefix = hashed_key[:3]
    if prefix in hash_buff:
        hash_buff[prefix].append((hashed_key, index))  # Append (hashed_key, index)
    else:
        hash_buff[prefix] = [(hashed_key, index)]  # Create new entry with (hashed_key, index)

# Bucket sort based on the first 6 bits of the hashed keys
sorted_buff = []
for prefix in sorted(hash_buff.keys()):
    for hashed_key, index in hash_buff[prefix]:
        sorted_buff.append((hashed_key, seq_buff.entries[index][1]))  # Append (hashed_key, value)

# Probing 10 samples from generated keys
print("Probing Samples:")
for _ in range(10):
    sample_key = random.choice(generated_keys_list)
    hashed_sample_key = hashlib.sha256(sample_key.encode()).hexdigest()
    found = False
    for entry in sorted_buff:
        if entry[0] == hashed_sample_key:
            found = True
            print("Key:", sample_key)
            print("Hashed Key:", hashed_sample_key)
            print("Value:", entry[1])
            print()
            break
    if not found:
        print("Key:", sample_key)
        print("Hashed Key:", hashed_sample_key)
        print("Value: Not Found")
        print()
