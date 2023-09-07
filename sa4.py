import queue
import hashlib
import math
import time
import threading
import random 
import mmh3

number_of_ssds = 4
msb_number = int(math.log(number_of_ssds, 2))

hashed_buffers = []
arrival_buffer = queue.Queue()

def generate_random_value():
    return bytes(random.getrandbits(8) for _ in range(4096))

for i in range(number_of_ssds):
    tq = queue.Queue()
    hashed_buffers.append(tq)

class key_value_pair:
    def __init__(self, key, value):
        self.key = key
        self.value = value

def hash_function(key):
    return mmh3.hash64(str(key), seed=0)[0]

def extract_msbs(value, num_bits):
    mask = (1 << num_bits) - 1
    msbs = (value >> (value.bit_length() - num_bits)) & mask
    return msbs

def input_func(arrival_buffer):
    #while True:
     #   key = input("Enter the logical block address (or 'exit' to stop): ")
      #  if key.lower() == 'exit':
      #      break
       # value = input("Enter the value: ")
       # kv_pair = key_value_pair(key, value)
       # arrival_buffer.put(kv_pair)
       # print(arrival_buffer.qsize())
    #time.sleep(1)
    for _ in range(10000):
        address = random.randint(0, 2**32 - 1)
        value = generate_random_value()
        kv_pair = key_value_pair(address,value)
        arrival_buffer.put(kv_pair)
        time.sleep(0.1)

    

def output(kv_pair):
    print("address sending to ssd:", kv_pair[0])

def bucket_sort(msbs, kv_pair, hashed_key):
    i = msbs
    print("Bucket sorting into: ", i)
    hkv_pair = (hashed_key, kv_pair.value)
    hashed_buffers[i].put(hkv_pair)
    print("buffer size:" ,hashed_buffers[i].qsize())

def kv_process(arrival_buffer):
    print("kv_process thread started.")
    while True:
        if arrival_buffer.empty():
            print("kv_process: Waiting for input...")
            time.sleep(5)
        else:
            kv_p = arrival_buffer.get()
            print("kv_process: Processing", kv_p.key)
            hashed_key = hash_function(kv_p.key)
            msbs = extract_msbs(hashed_key, msb_number)
            bucket_sort(msbs, kv_p, hashed_key)
            print("finished processing hash key:",hashed_key)
            print("arrival buffer after processsing: ",arrival_buffer.qsize())

def switch(hashed_buffers):
    print("switch thread started.")
    while True:
        for i in range(number_of_ssds):
            print("Switching for bucket", i)
            print("size of hashed bucket:",hashed_buffers[i].qsize())
            if not hashed_buffers[i].empty():
                kv_pair = hashed_buffers[i].get()
                output(kv_pair)
        time.sleep(5)



input_thread = threading.Thread(target=input_func, args=(arrival_buffer,),daemon=True)
sort_thread = threading.Thread(target=kv_process, args=(arrival_buffer,))
spit_thread = threading.Thread(target=switch, args=(hashed_buffers,),daemon=True)
input_thread.start()
sort_thread.start()
spit_thread.start()

input_thread.join()
sort_thread.join()
spit_thread.join()
