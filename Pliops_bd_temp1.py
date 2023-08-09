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

    def append(self, key, value):
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        self.entries.append((hashed_key, value))

    def search(self, key):
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        for entry in reversed(self.entries):
            if entry[0] == hashed_key:
                return entry[1]
        return None

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

for index in range(num_insertions):
    key = generate_random_string(key_length)
    value = generate_random_string(value_length)
    Welcome_Buff[key] = value  # Adding to the Welcome_Buff
    seq_buff.append(key, value)  # Adding to the SeqBuff
    hashed_key = hashlib.sha256(key.encode()).hexdigest()
    hash_buff[hashed_key] = index

# Bucket sort based on the first 6 bits of the hashed keys
sorted_buff = {}
for hashed_key, index in hash_buff.items():
    prefix = hashed_key[:6]
    if prefix in sorted_buff:
        sorted_buff[prefix].append((hashed_key, index))
    else:
        sorted_buff[prefix] = [(hashed_key, index)]

# Calculate the number of elements in each bucket
bucket_sizes = [len(entries) for entries in sorted_buff.values()]

# Plot the list of buckets
plt.plot(bucket_sizes,'bo')
plt.xlabel("Bucket Index")
plt.ylabel("Number of Elements")
plt.title("Bucket Sizes After Bucket Sort")
plt.show()

