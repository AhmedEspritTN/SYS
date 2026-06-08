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
    """Quick parallel file processing demonstration"""
    print("\n" + "="*60)
    print("QUICK START: Parallel File Processing")
    print("="*60)

    from file_processing import ParallelFileProcessor, create_sample_file

    sample_file = Path(__file__).parent / "sample_input.bin"
    create_sample_file(sample_file, size_mb=2)

    processor = ParallelFileProcessor(
        file_path=sample_file,
        chunk_size_kb=512,
        num_processes=2,
        num_threads=2,
    )

    print("\n1. Sequential File Processing")
    print("-" * 40)
    seq_result = processor.process_sequential()
    print(f"  Chunks: {seq_result.chunks_processed}")
    print(f"  Time: {seq_result.total_time:.2f} seconds")
    print(f"  SHA-256: {seq_result.file_sha256[:16]}...")

    print("\n2. Multiprocessing File Processing")
    print("-" * 40)
    mp_result = processor.process_with_multiprocessing()
    print(f"  Chunks: {mp_result.chunks_processed}")
    print(f"  Time: {mp_result.total_time:.2f} seconds")
    print(f"  SHA-256: {mp_result.file_sha256[:16]}...")

    print("\n3. Multithreading File Processing")
    print("-" * 40)
    mt_result = processor.process_with_multithreading()
    print(f"  Chunks: {mt_result.chunks_processed}")
    print(f"  Time: {mt_result.total_time:.2f} seconds")
    print(f"  SHA-256: {mt_result.file_sha256[:16]}...")

    if seq_result.total_time > 0:
        print(f"\n  Multiprocessing speedup: {seq_result.total_time / mp_result.total_time:.2f}x")
        print(f"  Multithreading speedup: {seq_result.total_time / mt_result.total_time:.2f}x")


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
