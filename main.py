import threading
import random

LOWER_NUM = 1
UPPER_NUM = 10000
BUFFER_SIZE = 100
MAX_COUNT = 10000

class BoundedBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = []
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def insert(self, item):
        with self.not_full:
            while len(self.buffer) >= self.size:
                self.not_full.wait()
            self.buffer.append(item)
            self.not_empty.notify()

    def remove_even(self):
        with self.not_empty:
            while not self.buffer or self.buffer[-1] % 2 != 0:
                self.not_empty.wait()
            item = self.buffer.pop()
            self.not_full.notify()
            return item

    def remove_odd(self):
        with self.not_empty:
            while not self.buffer or self.buffer[-1] % 2 == 0:
                self.not_empty.wait()
            item = self.buffer.pop()
            self.not_full.notify()
            return item

def producer(buffer):
    for _ in range(MAX_COUNT):
        num = random.randint(LOWER_NUM, UPPER_NUM)
        with open('all.txt', 'a') as f:
            f.write(str(num) + '\n')
        buffer.insert(num)

def customer_even(buffer):
    while True:
        num = buffer.remove_even()
        with open('even.txt', 'a') as f:
            f.write(str(num) + '\n')
        if len(open('even.txt').readlines()) == MAX_COUNT // 2:
            break

def customer_odd(buffer):
    while True:
        num = buffer.remove_odd()
        with open('odd.txt', 'a') as f:
            f.write(str(num) + '\n')
        if len(open('odd.txt').readlines()) == MAX_COUNT // 2:
            break

if __name__ == "__main__":
    buffer = BoundedBuffer(BUFFER_SIZE)

    producer_thread = threading.Thread(target=producer, args=(buffer,))
    customer_even_thread = threading.Thread(target=customer_even, args=(buffer,))
    customer_odd_thread = threading.Thread(target=customer_odd, args=(buffer,))

    producer_thread.start()
    customer_even_thread.start()
    customer_odd_thread.start()

    producer_thread.join()
    customer_even_thread.join()
    customer_odd_thread.join()