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
        logical_block_address = input("Enter a logical block address (64 characters): ")
        logical_block_address = logical_block_address[:64].ljust(64, '0')  # Limit to 64 characters and pad with zeros
        value = input("Enter a value (up to 4KB): ")
        value_size = len(value.encode())  # Size in bytes
        if value_size > VALUE_BLOCK_SIZE:
            print("Value size cannot exceed 4KB.")
            continue
        
        data_queue.put((logical_block_address, value))
        time.sleep(1)  # Just to avoid overwhelming the console

# Start the input_reader thread
input_thread = threading.Thread(target=input_reader, daemon=True)
input_thread.start()

# Main loop to process data from the queue
while True:
    try:
        logical_block_address, value = data_queue.get(timeout=1)  # Wait for up to 1 second
        print(f"Received: Logical Block Address: {logical_block_address}, Value: {value}")
        data_queue.task_done()  # Mark the task as done
    except queue.Empty:
        pass  # No data in the queue, continue processing or do other tasks
