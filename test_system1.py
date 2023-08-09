import random
import string

class KeyValuePairQueue:
  def __init__(self):
    self._queue = []

  def enqueue(self, key, value):
    """Enqueues a key value pair into the queue."""
    self._queue.append((key, value))

  def dequeue(self):
    """Dequeues the first element from the queue."""
    if not self._queue:
      return None
    return self._queue.pop(0)

  def peek(self):
    """Returns the first element from the queue without dequeuing it."""
    if not self._queue:
      return None
    return self._queue[0]

  def get_bottom_element(self):
    """Returns the element at the bottom of the queue."""
    if not self._queue:
      return None
    return self._queue[-1]

def generate_random_key_value_pair():
  """Generates a random 32 bit key and a random string value attached to it."""
  key = random.randint(0, 2**32 - 1)
  value = ''.join([chr(random.randint(97, 122)) for _ in range(10)])
  return key, value

if __name__ == '__main__':
  queue = KeyValuePairQueue()
  for _ in range(10):
    key, value = generate_random_key_value_pair()
    queue.enqueue(key, value)


  print('Bottom element:', queue.get_bottom_element())
