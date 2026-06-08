"""
QUICK START EXAMPLE
Simple, focused examples to understand each concept quickly.
Run this file to see demonstrations of key concepts.
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def quick_start_ipc():
    """Quick IPC demonstration"""
    print("\n" + "="*60)
    print("QUICK START: Interprocess Communication")
    print("="*60)
    
    from multiprocessing import Process, Pipe, Queue
    
    # Example 1: Simple Pipe
    print("\n1. Pipe Communication (1-to-1)")
    print("-" * 40)
    parent_conn, child_conn = Pipe()
    
    def pipe_worker(conn):
        msg = conn.recv()
        print(f"  Child received: '{msg}'")
        conn.send(f"Echo: {msg}")
    
    p = Process(target=pipe_worker, args=(child_conn,))
    p.start()
    
    parent_conn.send("Hello from parent!")
    response = parent_conn.recv()
    print(f"  Parent got: '{response}'")
    
    p.join()
    
    # Example 2: Simple Queue
    print("\n2. Queue Communication (Many-to-Many)")
    print("-" * 40)
    queue = Queue()
    
    def producer(q, item_id):
        for i in range(2):
            item = f"Item_{item_id}_{i}"
            q.put(item)
            print(f"  Producer {item_id}: Created '{item}'")
    
    def consumer(q, consumer_id):
        for _ in range(2):
            item = q.get(timeout=2)
            print(f"  Consumer {consumer_id}: Got '{item}'")
    
    # Simple sequential version for quick demo
    producer(queue, 1)
    for i in range(2):
        consumer(queue, 1)


def quick_start_synchronization():
    """Quick synchronization demonstration"""
    print("\n" + "="*60)
    print("QUICK START: Synchronization")
    print("="*60)
    
    import threading
    from threading import Semaphore, Lock
    
    # Example 1: Semaphore (Resource Control)
    print("\n1. Semaphore (Limit to 2 concurrent users)")
    print("-" * 40)
    sem = Semaphore(2)
    
    def worker_sem(worker_id):
        print(f"  Worker {worker_id}: Trying to acquire...")
        sem.acquire()
        print(f"  Worker {worker_id}: Got resource!")
        time.sleep(0.1)
        sem.release()
        print(f"  Worker {worker_id}: Released resource")
    
    threads = []
    for i in range(4):
        t = threading.Thread(target=worker_sem, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Example 2: Lock (Protect Shared Data)
    print("\n2. Lock (Protect shared counter)")
    print("-" * 40)
    counter = 0
    lock = Lock()
    
    def increment():
        nonlocal counter
        with lock:
            old = counter
            counter = old + 1
    
    threads = []
    for i in range(3):
        for _ in range(3):
            t = threading.Thread(target=increment)
            threads.append(t)
            t.start()
    
    for t in threads:
        t.join()
    
    print(f"  Final counter: {counter} (should be 9)")


def quick_start_parallel():
    """Quick parallel processing demonstration"""
    print("\n" + "="*60)
    print("QUICK START: Parallel Processing")
    print("="*60)
    
    from multiprocessing import Pool, cpu_count
    
    def fibonacci(n):
        """Compute Fibonacci number (CPU-bound)"""
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # Single process
    print("\n1. Sequential Processing")
    print("-" * 40)
    start = time.time()
    results = [fibonacci(30) for _ in range(3)]
    seq_time = time.time() - start
    print(f"  Results: {results}")
    print(f"  Time: {seq_time:.2f} seconds")
    
    # Multiple processes
    print("\n2. Parallel Processing (Multiprocessing)")
    print("-" * 40)
    start = time.time()
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(fibonacci, [30] * 3)
    par_time = time.time() - start
    print(f"  Results: {results}")
    print(f"  Time: {par_time:.2f} seconds")
    print(f"  Speedup: {seq_time/par_time:.2f}x")


def quick_start_classic_problem():
    """Quick classic problem demonstration"""
    print("\n" + "="*60)
    print("QUICK START: Classic Problem - Dining Philosophers")
    print("="*60)
    
    import threading
    
    class SimpleDiningPhilosophers:
        def __init__(self, n=3):
            self.n = n
            self.forks = [threading.Semaphore(1) for _ in range(n)]
        
        def eat(self, philosopher_id):
            left_fork = philosopher_id
            right_fork = (philosopher_id + 1) % self.n
            
            print(f"  Philosopher {philosopher_id}: Hungry...")
            self.forks[left_fork].acquire()
            print(f"  Philosopher {philosopher_id}: Got left fork")
            self.forks[right_fork].acquire()
            print(f"  Philosopher {philosopher_id}: Got right fork, EATING!")
            time.sleep(0.05)
            self.forks[left_fork].release()
            self.forks[right_fork].release()
            print(f"  Philosopher {philosopher_id}: Finished eating")
    
    dining = SimpleDiningPhilosophers(n=3)
    
    print("\n3 Philosophers with 3 Forks")
    print("-" * 40)
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=dining.eat, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("  All philosophers finished!")


def main():
    """Run all quick start examples"""
    print("\n" + "#"*60)
    print("# QUICK START: PARALLEL PROCESSING CONCEPTS")
    print("#"*60)
    
    try:
        quick_start_ipc()
    except Exception as e:
        print(f"\nError in IPC demo: {e}")
    
    try:
        quick_start_synchronization()
    except Exception as e:
        print(f"\nError in Synchronization demo: {e}")
    
    try:
        quick_start_parallel()
    except Exception as e:
        print(f"\nError in Parallel demo: {e}")
    
    try:
        quick_start_classic_problem()
    except Exception as e:
        print(f"\nError in Classic Problem demo: {e}")
    
    print("\n" + "#"*60)
    print("# QUICK START COMPLETED!")
    print("#"*60)
    print("\nNext steps:")
    print("  1. Read INSTRUCTIONS.md for detailed explanations")
    print("  2. Run: python examples/run_all_examples.py (full suite)")
    print("  3. Check REQUIREMENTS.md for technical details")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()
