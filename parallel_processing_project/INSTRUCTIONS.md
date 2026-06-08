# PARALLEL PROCESSING & BENCHMARKING PROJECT

## Quick Start

### Prerequisites
- Python 3.8 or higher
- No external dependencies required (uses only standard library)

### Run Everything at Once
```bash
cd parallel_processing_project
python examples/run_all_examples.py
```

This will run all demonstrations automatically.

---

## Project Structure

```
parallel_processing_project/
├── ipc_communication.py          # IPC: Pipes, Queues, Shared Memory
├── synchronization.py             # Semaphores & Classic Problems
├── parallel_processing.py         # Multiprocessing & Multithreading
└── examples/
    ├── run_all_examples.py        # Master example runner
    └── real_world_examples.py     # Video & File processing
```

---

## Running Individual Modules

### 1. IPC Communication Examples
```bash
python parallel_processing_project/ipc_communication.py
```

**What it demonstrates:**
- **Pipe Communication**: Direct process-to-process communication
  - Parent and child process exchange messages through a pipe
  - Bidirectional communication (two endpoints)
  
- **Queue Communication**: Multi-process message passing
  - Multiple producers create items
  - Multiple consumers process items
  - Thread-safe and process-safe queues

- **Shared Memory**: Direct memory sharing between processes
  - Shared integer counter (atomic operations)
  - Shared arrays for data sharing
  - Thread-safe access with locks

**Output Example:**
```
============================================================
PIPE COMMUNICATION EXAMPLE
============================================================
Parent: Processed: Hello (by Worker 1)
Parent: Processed: Parallel (by Worker 1)
...
```

---

### 2. Synchronization & Classic Problems
```bash
python parallel_processing_project/synchronization.py
```

**What it demonstrates:**

- **Dining Philosophers Problem**
  - 5 philosophers at a table with 5 forks
  - Each philosopher needs 2 forks to eat
  - Solution: State machine + semaphore-based synchronization
  - Avoids deadlock through careful fork acquisition
  - States: THINKING → HUNGRY → EATING

- **Sleeping Barber Problem**
  - Barber serves customers from waiting room
  - Limited waiting chairs (default: 3)
  - Full waiting room = customers leave
  - Solution: Semaphores for customer queue and barber availability

- **Producer-Consumer Problem**
  - Multiple producers create items
  - Multiple consumers process items
  - Bounded buffer with capacity constraints
  - Synchronization via semaphores for empty/full slots

**Output Example:**
```
============================================================
DINING PHILOSOPHERS PROBLEM
============================================================
Philosopher 0: Thinking...
Philosopher 0: Hungry, trying to get forks...
Philosopher 0: Eating! (cycle 1)
Philosopher 0: Finished eating
```

---

### 3. Multiprocessing & Multithreading
```bash
python parallel_processing_project/parallel_processing.py
```

**What it demonstrates:**

- **Multiprocessing (CPU-bound tasks)**
  - Creates multiple worker processes
  - Each process has its own Python interpreter (bypasses GIL)
  - Fibonacci computation: actual CPU-intensive work
  - Configurable number of processes
  - Best for: heavy computations, image processing, data analysis

- **Multithreading (I/O-bound tasks)**
  - Creates multiple worker threads
  - Shared memory within process
  - Simulates I/O operations (file, network)
  - Good for: API calls, file I/O, network operations

- **Benchmarking & Speedup**
  - Sequential baseline: 1 worker only
  - Multiprocessing: 4 workers (or cpu_count())
  - Calculates actual speedup improvement
  - Measures throughput and performance

**Configuration:**
```python
config = ProcessingConfig(
    num_processes=4,      # Number of worker processes
    num_threads=1,        # Number of threads per process
    workload_size=100     # Workload in KB/units
)
```

**Output Example:**
```
============================================================
BENCHMARKING: Sequential vs Parallel
============================================================
Running sequential processing...
Sequential time: 2.45 seconds

Running multiprocessing...
Multiprocessing time: 0.89 seconds

Speedup: 2.75x
```

---

### 4. Real-World Examples
```bash
python parallel_processing_project/examples/real_world_examples.py
```

**What it demonstrates:**

#### 4a. Video Processing
- Simulates processing 100 video frames
- Each frame: object detection, edge detection, etc.
- Processes frames in parallel
- Measures FPS (frames per second)
- Compares sequential vs parallel throughput

**Configuration:**
```python
processor = VideoProcessor(num_workers=4)
processor.benchmark(num_frames=100)
```

**Output Example:**
```
Sequential processing (1 worker):
  Total time: 1.23 seconds
  FPS: 81.30 frames/sec
  Per-frame: 12.30 ms

Parallel processing (4 workers):
  Total time: 0.42 seconds
  FPS: 238.10 frames/sec
  Per-frame: 4.20 ms

Speedup: 2.93x faster with 4 workers
```

#### 4b. Large File Processing
- Simulates processing 50 MB files
- Splits file into chunks (1 MB each)
- Processes chunks in parallel
- Calculates throughput (MB/s)
- Useful for: log analysis, data processing, compression

**Configuration:**
```python
processor = LargeFileProcessor(
    chunk_size_kb=1024,   # 1 MB chunks
    num_workers=4
)
processor.benchmark(total_size_mb=50)
```

**Output Example:**
```
Sequential processing:
  Time: 1.05 seconds
  Throughput: 47.62 MB/s
  Chunks: 50

Parallel processing (4 workers):
  Time: 0.31 seconds
  Throughput: 161.29 MB/s
  Chunks: 50

Speedup: 3.39x faster
```

---

## Running Examples in Different Ways

### Option A: Run All at Once (Recommended)
```bash
python examples/run_all_examples.py
```
Takes ~30-60 seconds, shows everything.

### Option B: Run Individual Examples
```bash
# IPC only
python ipc_communication.py

# Synchronization only
python synchronization.py

# Parallel processing only
python parallel_processing.py

# Real-world examples only
python examples/real_world_examples.py
```

### Option C: Create Custom Script
```python
# my_experiment.py
from parallel_processing_project.parallel_processing import ConfigurableParallelProcessor, ProcessingConfig

# Configure for YOUR system
config = ProcessingConfig(
    num_processes=8,      # More workers
    num_threads=4,
    workload_size=256     # Larger workload
)

processor = ConfigurableParallelProcessor(config)

# Benchmark different task counts
for num_tasks in [4, 8, 16]:
    print(f"\n--- Processing {num_tasks} tasks ---")
    result = processor.process_with_multiprocessing(num_tasks)
    print(f"Time: {result['total_time']:.2f}s")
```

Run with:
```bash
python my_experiment.py
```

---

## Key Concepts Explained

### 1. Interprocess Communication (IPC)

**Pipes**
- One-way or two-way connection between 2 processes
- Like a buffer with read and write ends
- Use when: 1-to-1 producer/consumer communication
```python
parent_conn, child_conn = Pipe()
parent_conn.send("message")
received = child_conn.recv()
```

**Queues**
- Safe messaging for multiple processes
- FIFO (First In, First Out) order
- Multiple producers/consumers
- Use when: many processes need to exchange data
```python
queue = Queue()
queue.put(item)
item = queue.get(timeout=1)
```

**Shared Memory**
- Direct memory access between processes
- Requires synchronization (locks)
- Most efficient but requires careful handling
- Use when: high-performance data sharing needed
```python
counter = Value('i', 0)  # Shared integer
array = Array('d', [0]*10)  # Shared doubles
```

### 2. Synchronization Primitives

**Semaphores**
- Counter with P (acquire/wait) and V (release) operations
- Value >= 0 at all times
- Blocks when counter = 0
- Binary semaphore (0/1): like a lock
- Counting semaphore (0+): multiple resources
```python
sem = Semaphore(5)  # 5 available resources
sem.acquire()       # Decrement
# Use resource
sem.release()       # Increment
```

**Locks/Mutexes**
- Ensure only 1 thread/process in critical section
- Deadlock if not released properly
```python
lock = Lock()
with lock:
    # Protected code
    shared_data.append(item)
```

**Condition Variables**
- Allow threads to wait for specific conditions
- More efficient than polling
```python
condition = Condition()
with condition:
    condition.wait()    # Wait for signal
    condition.notify()  # Signal waiting threads
```

### 3. When to Use What

**Use Multiprocessing When:**
- Task is CPU-intensive (calculations, data processing)
- Need true parallelism (multiple cores)
- GIL is a bottleneck
- Long-running processes
```python
# CPU-bound: factorial, Fibonacci, sorting
result = fibonacci(40)
```

**Use Multithreading When:**
- Task involves I/O (network, files, databases)
- Fine-grained synchronization needed
- Less memory required (vs processes)
- Frequent communication between workers
```python
# I/O-bound: HTTP requests, file reads
response = requests.get(url)
```

**Speedup Expectations:**
- CPU-bound + multiprocessing: Near linear speedup (N tasks on N cores ≈ N× faster)
- I/O-bound + multithreading: Can exceed core count (10 threads on 4 cores for network)
- Sequential baseline: Always slowest for parallelizable work

---

## Performance Tips

1. **Profile First**
   ```python
   import timeit
   time = timeit.timeit(func, number=100)
   ```

2. **Match Workers to Task**
   - CPU-bound: processes = cpu_count()
   - I/O-bound: threads = 2-4 × cpu_count()

3. **Avoid Synchronization Overhead**
   - Too many locks = slowdown
   - Design for minimal contention
   - Use lock-free data structures where possible

4. **Chunk Your Work**
   - Optimal chunk size: task_time ≈ 100ms
   - Too small: scheduling overhead
   - Too large: uneven load distribution

5. **Benchmark Real Scenarios**
   - Test with your actual data sizes
   - Real-world workloads vary
   - Consider system load from other processes

---

## Troubleshooting

### Issue: "RuntimeError: An attempt has been made to start a new process..."
**Solution:** Wrap multiprocessing code in `if __name__ == "__main__":`
```python
if __name__ == "__main__":
    processor.process_video_parallel(100)
```

### Issue: "Deadlock" (program hangs)
**Causes:**
- Circular wait for locks
- Semaphore never released
- Forget to release acquired fork/resource

**Prevention:**
- Always use `with lock:` context managers
- Never hold multiple locks simultaneously
- Test with fewer processes first

### Issue: "Slow parallel code"
**Causes:**
- Task too small (overhead > speedup)
- I/O-bound using multiprocessing
- Excessive synchronization
- Not enough workers

**Debug:**
```python
# Measure per-task time
start = time.time()
result = task(item)
print(f"Task time: {time.time() - start}s")

# Should be >> 10ms for parallelism to help
```

### Issue: "Memory usage high"
**Causes:**
- Too many processes
- Copying data to each process
- Shared memory not released

**Solution:**
- Reduce num_processes
- Use generators for data
- Ensure cleanup in finally blocks

---

## Further Learning

**Recommended Topics:**
1. Process pooling for production use
2. Async/await for coroutines (single thread, many I/O tasks)
3. Lock-free data structures
4. Distributed computing (multi-machine)
5. GPU acceleration with multiprocessing

**Books:**
- "Python Cookbook" - Recipes section
- "Effective Python" - Chapters on Concurrency

**Online Resources:**
- Python docs: https://docs.python.org/3/library/multiprocessing.html
- Threading docs: https://docs.python.org/3/library/threading.html

---

## Assignment Checklist

This project covers all required criteria:

✓ **Multiprocessing & Multithreading**
  - Configurable number of processes (default: cpu_count())
  - Configurable number of threads (default: 4)
  - Examples with 2, 4, 8 workers

✓ **IPC Techniques**
  - Pipes: ipc_communication.py
  - Queues: ipc_communication.py
  - Shared Memory: ipc_communication.py

✓ **Synchronization with Semaphores**
  - Semaphores used in all synchronization examples
  - Mutex locks for shared data
  - Proper release with context managers

✓ **Classic Problems**
  - Dining Philosophers: synchronization.py (dining philosophers section)
  - Sleeping Barber: synchronization.py (sleeping barber section)

✓ **Code Quality**
  - English comments throughout
  - Clear function documentation
  - Error handling

✓ **Deliverables**
  - Source code: ✓
  - Runnable examples: ✓
  - Technical documentation: ✓ (this file)

---

## Running on Different Systems

**Windows:**
```bash
python examples/run_all_examples.py
```

**Linux/Mac:**
```bash
python3 examples/run_all_examples.py
```

**With Specific Python Version:**
```bash
python3.10 examples/run_all_examples.py
```

---

## Expected Output

All scripts will produce console output showing:
1. Module being executed
2. Progress indicators
3. Timing measurements
4. Speedup calculations
5. Summary of results

Execution times vary based on:
- Your CPU speed
- System load
- RAM available
- Cooling (thermal throttling)

Typical execution time: 30-60 seconds for full test suite.

---

**Project Completed: 2026**
**Status: Ready for deployment and evaluation**
