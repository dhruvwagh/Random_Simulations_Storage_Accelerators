import queue
import threading
import time

# Create a thread-safe queue
data_queue = queue.Queue()

# Define the value block size in bytes
VALUE_BLOCK_SIZE = 4 * 1024  # 4KB

# Function to continuously read user input and append values to the queue
def input_reader():
    while True:
        try:
            key = int(input("Enter a key (integer): "))
            if key < 0 or key >= 2**64:
                print("Key must be a non-negative integer less than 2^64.")
                continue
            
            value = input("Enter a value (up to 4KB): ")
            value_size = len(value.encode())  # Size in bytes
            if value_size > VALUE_BLOCK_SIZE:
                print("Value size cannot exceed 4KB.")
                continue
            
            binary_key = format(key, '064b')  # Convert key to 64-bit binary string
            data_queue.put((binary_key, value))
            time.sleep(1)  # Just to avoid overwhelming the console
        
        except ValueError:
            print("Invalid input. Key must be a non-negative integer.")

# Start the input_reader thread
input_thread = threading.Thread(target=input_reader, daemon=True)
input_thread.start()

# Main loop to process data from the queue
while True:
    try:
        binary_key, value = data_queue.get(timeout=1)  # Wait for up to 1 second
        print(f"Received: Binary Key: {binary_key}, Value: {value}")
        data_queue.task_done()  # Mark the task as done
    except queue.Empty:
        pass  # No data in the queue, continue processing or do other tasks