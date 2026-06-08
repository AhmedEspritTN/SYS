"""
IPC (Interprocess Communication) Utilities Module
Demonstrates: Pipes, Queues, and Shared Memory Segments
"""

import multiprocessing as mp
from multiprocessing import Process, Pipe, Queue
import time
from typing import Any, Callable


class PipeCommunication:
    """
    Pipe-based communication between two processes.
    A pipe is a connection between two processes with two endpoints.
    """
    
    def __init__(self):
        """Initialize a bidirectional pipe"""
        self.parent_conn, self.child_conn = Pipe()
    
    def send_data(self, data: Any) -> None:
        """Send data through the pipe"""
        self.parent_conn.send(data)
    
    def receive_data(self) -> Any:
        """Receive data from the pipe"""
        if self.parent_conn.poll(timeout=1):
            return self.parent_conn.recv()
        return None
    
    @staticmethod
    def worker_pipe(conn, worker_id: int):
        """
        Worker function that receives from pipe and sends response.
        
        Args:
            conn: Child connection from pipe
            worker_id: Worker identifier
        """
        for i in range(5):
            # Receive data from parent
            data = conn.recv()
            print(f"Worker {worker_id}: Received '{data}'")
            
            # Process and send back
            result = f"Processed: {data} (by Worker {worker_id})"
            conn.send(result)
        
        conn.close()


class QueueCommunication:
    """
    Queue-based communication for multiple producers/consumers.
    Queues are thread-safe and process-safe.
    """
    
    def __init__(self, maxsize: int = 10):
        """
        Initialize a queue for IPC.
        
        Args:
            maxsize: Maximum queue size (0 = unlimited)
        """
        self.queue = Queue(maxsize=maxsize)
    
    def put_item(self, item: Any) -> None:
        """Add item to queue"""
        self.queue.put(item)
    
    def get_item(self, timeout: int = 1) -> Any:
        """Retrieve item from queue"""
        try:
            return self.queue.get(timeout=timeout)
        except mp.queue.Empty:
            return None
    
    @staticmethod
    def producer_worker(queue, producer_id: int, num_items: int):
        """
        Producer worker that puts items in queue.
        
        Args:
            queue: Shared queue
            producer_id: Producer identifier
            num_items: Number of items to produce
        """
        for i in range(num_items):
            item = f"Item_{producer_id}_{i}"
            queue.put(item)
            print(f"Producer {producer_id}: Produced '{item}'")
            time.sleep(0.1)
    
    @staticmethod
    def consumer_worker(queue, consumer_id: int, num_items: int):
        """
        Consumer worker that gets items from queue.
        
        Args:
            queue: Shared queue
            consumer_id: Consumer identifier
            num_items: Number of items to consume
        """
        for _ in range(num_items):
            item = queue.get(timeout=2)
            print(f"Consumer {consumer_id}: Consumed '{item}'")
            time.sleep(0.05)


class SharedMemoryData:
    """
    Shared memory segment for inter-process data sharing.
    Uses multiprocessing.Value and Array for shared data structures.
    """
    
    def __init__(self):
        """Initialize shared memory segments"""
        # Shared value (counter)
        self.counter = mp.Value('i', 0)  # 'i' = signed integer
        
        # Shared array
        self.shared_array = mp.Array('d', [0.0] * 10)  # 'd' = double
        
        # Lock for synchronization
        self.lock = mp.Lock()
    
    def increment_counter(self) -> None:
        """Thread-safe counter increment"""
        with self.lock:
            self.counter.value += 1
    
    def get_counter(self) -> int:
        """Get counter value"""
        with self.lock:
            return self.counter.value
    
    def update_array_element(self, index: int, value: float) -> None:
        """Update shared array element"""
        with self.lock:
            if 0 <= index < len(self.shared_array):
                self.shared_array[index] = value
    
    def get_array(self) -> list:
        """Get copy of shared array"""
        with self.lock:
            return list(self.shared_array)
    
    @staticmethod
    def worker_shared_memory(shared_data, worker_id: int, iterations: int):
        """
        Worker that modifies shared memory.
        
        Args:
            shared_data: SharedMemoryData instance
            worker_id: Worker identifier
            iterations: Number of iterations
        """
        for i in range(iterations):
            shared_data.increment_counter()
            shared_data.update_array_element(worker_id, worker_id * (i + 1))
            time.sleep(0.01)


def demonstrate_pipes():
    """Demonstrate pipe communication"""
    print("\n" + "="*60)
    print("PIPE COMMUNICATION EXAMPLE")
    print("="*60)
    
    pipe = PipeCommunication()
    
    # Create worker process
    p = Process(target=PipeCommunication.worker_pipe, 
                args=(pipe.child_conn, 1))
    p.start()
    
    # Send and receive through pipe
    messages = ["Hello", "Parallel", "Processing", "Works", "Great"]
    for msg in messages:
        pipe.send_data(msg)
        time.sleep(0.1)
        result = pipe.receive_data()
        print(f"Parent: {result}")
    
    p.join()


def demonstrate_queues():
    """Demonstrate queue communication"""
    print("\n" + "="*60)
    print("QUEUE COMMUNICATION EXAMPLE")
    print("="*60)
    
    queue = QueueCommunication(maxsize=5)
    
    # Create producer and consumer processes
    producers = []
    consumers = []
    
    for i in range(2):
        p = Process(target=QueueCommunication.producer_worker,
                   args=(queue.queue, i, 3))
        producers.append(p)
        p.start()
    
    for i in range(2):
        c = Process(target=QueueCommunication.consumer_worker,
                   args=(queue.queue, i, 3))
        consumers.append(c)
        c.start()
    
    for p in producers + consumers:
        p.join()


def demonstrate_shared_memory():
    """Demonstrate shared memory communication"""
    print("\n" + "="*60)
    print("SHARED MEMORY EXAMPLE")
    print("="*60)
    
    shared_data = SharedMemoryData()
    
    # Create worker processes
    processes = []
    for i in range(3):
        p = Process(target=SharedMemoryData.worker_shared_memory,
                   args=(shared_data, i, 5))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print(f"Final counter value: {shared_data.get_counter()}")
    print(f"Final array: {shared_data.get_array()}")


if __name__ == "__main__":
    demonstrate_pipes()
    demonstrate_queues()
    demonstrate_shared_memory()
