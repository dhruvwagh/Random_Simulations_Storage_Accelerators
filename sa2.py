import queue
import hashlib
import math
import time
import threading

number_of_ssds = 4
msb_number=int(math.log(number_of_ssds,2))

hashed_buffers=[]

for i in range(msb_number):
    tq= queue.Queue()
    hashed_buffers.append(tq)

class key_value_pair:
    def __init__(self,key,value):
        self.key= key
        self.value = value
    def display(self):
        print("Key: ", self.key," Value: ", self.value)

arrival_buffer=queue.Queue()

def hash_function(key):
    return hashlib.sha256(key).digest()[:8]

def extract_msbs(value, num_bits):
    mask = (1 << num_bits) - 1 
    msbs = (value >> (value.bit_length() - num_bits)) & mask
    return msbs

def input(arrival_buffer):
    while True:
        key = input("Enter the logical block address (or 'exit' to stop): ")
        if key.lower() == 'exit':
            break
        value = input("Enter the value: ")
        kv_pair = key_value_pair(key, value)
        arrival_buffer.put(kv_pair)

def output(kv_pair):
    print("Hashed Key: ",kv_pair[0],"Value: ",kv_pair[1])

def bucket_sort(msbs,kv_pair,hashed_key):
    i= int(msbs, 2)
    hkv_pair= (hashed_key,kv_pair.value)
    hashed_buffers[i].put(hkv_pair)


def kv_process(arrival_buffer):
    while not arrival_buffer.empty:
        kv_p = arrival_buffer.get()
        hashed_key=hash_function(kv_p.key)
        msbs = extract_msbs(hashed_key,msb_number)
        bucket_sort(msbs,kv_p,hashed_key)

def switch(hashed_buffers):
    for i in hashed_buffers:
        kv_pair = i.get()
        output(kv_pair)

input_thread = threading.Thread(target=input,args=(arrival_buffer,))
sort_thread = threading.Thread(target=kv_process,args=(arrival_buffer,))
spit_thread = threading.Thread(target = switch,args=(hashed_buffers,))

input_thread.start()
sort_thread.start()
spit_thread.start()
