# Technical Guide — How We Implemented Each Course Requirement

This document explains **what we did**, **where in the code**, and **which Python libraries** we used.

**Project focus:** parallel file processing (IntegrityCheck) — read a file in chunks, compute SHA-256, compare sequential vs parallel modes.

**Authors:** Hassen Moussi & Ahmed Arfaoui

---

## Libraries Used (Summary)

| Library | Module in Python | Used for |
|---------|------------------|----------|
| `multiprocessing` | stdlib | Process pools, pipes, queues, shared memory |
| `threading` | stdlib | Threads, semaphores, locks |
| `queue` | stdlib | Thread-safe task queues |
| `importlib` | stdlib | Dynamic loading of external solutions |
| `hashlib` | stdlib | SHA-256 checksums |
| `dataclasses` | stdlib | Configuration objects |
| `pathlib` | stdlib | File paths |
| `argparse` | stdlib | Command-line options |

**No external packages** (no pip install needed for the core application).

---

## Project Structure (Quick Map)

```
parallel_processing_project/
├── client.py                      ← User application (menu)
├── file_processing.py             ← Core: multiprocessing + multithreading on files
├── sleeping_barber_processor.py   ← Sleeping Barber applied to file chunks
├── parallel_processing.py         ← CLI + config + software loader
├── sample_solution.py             ← External plugin example
├── ipc_communication.py           ← IPC demos (pipes, queues, shared memory)
└── synchronization.py             ← Semaphore classic problems (demos)
```

**Important:** The **main application** is file processing (`client.py`, `file_processing.py`). IPC and classic sync problems live in **separate demo modules** that prove the OS concepts for the course.

---

## What is SHA-256?

**SHA-256** (Secure Hash Algorithm, 256-bit) is a cryptographic hash function. It takes any file (or any data) as input and produces a **fixed fingerprint** of exactly **64 hexadecimal characters** (256 bits).

### In simple terms
- Think of it as a **digital fingerprint** of a file.
- If the file changes by even **one bit**, the SHA-256 value changes completely.
- If two files have the **same SHA-256**, they are considered **identical** (for practical purposes).

### Why we use it in IntegrityCheck
After copying or downloading a large file, we need to know: *“Did the file arrive exactly as sent?”*  
Our app reads the file in chunks, hashes each chunk, then computes one **full-file SHA-256**. If sequential, multiprocessing, multithreading, and Sleeping Barber modes all return the **same** checksum, we know:
1. Parallel processing did not corrupt the data.
2. The file integrity is verified.

### Example
```
File: sample_input.bin (20 MB)
SHA-256: aef406dbd745899858bb713fd5b137c50fb9dc9c85576b99a82af66989509bc5
```
If you run the app again on the same file, you should get the **same** hash. If the file is damaged, the hash will be different.

### Where in our code
**File:** `file_processing.py`

```python
import hashlib

# Per chunk
checksum = hashlib.sha256(data).hexdigest()

# Full file
sha256 = hashlib.sha256()
sha256.update(data)
file_hash = sha256.hexdigest()
```

**Library:** Python standard library `hashlib` — no extra install required.

### SHA-256 is not encryption
- It does **not** hide or protect the file content.
- It only **identifies** the content and detects changes.
- You cannot recover the original file from the hash alone.

---

## 1. Multiprocessing & Multithreading (Configurable)

### Requirement
> The number of processes and the number of threads must be configurable.

### What we did
- User can set **how many processes** (multiprocessing) and **how many threads** (multithreading).
- Same file is processed in parallel; results include timing and SHA-256.
- Configuration works via:
  - Interactive client (`client.py`)
  - Command line (`parallel_processing.py`)
  - `ProcessingConfig` dataclass

### Libraries
```python
import multiprocessing as mp   # processes, Pool
import threading               # threads, Lock, Semaphore
import queue                   # thread-safe Queue
```

### Where in the code

#### A) Configuration object
**File:** `parallel_processing.py`

```python
@dataclass
class ProcessingConfig:
    num_processes: int      # configurable
    num_threads: int        # configurable
    chunk_size_kb: int = 1024
    file_path: Optional[str] = None
```

#### What is the difference between process, thread, and chunk?

These three words mean **different things**. In `ProcessingConfig`, **process** and **thread** are *workers*; **chunk** is *work to do*.

---

**Chunk** — a **piece of the file** (data, not a worker)

| | |
|---|---|
| **What** | A small slice of the file (default **1024 KB = 1 MB**) |
| **Why** | A 20 MB file is too big to handle as one block; we split it so many workers can work at the same time |
| **Setting** | `chunk_size_kb` in `ProcessingConfig` |
| **Example** | 20 MB file ÷ 1 MB chunks = **20 chunks** |
| **In code** | `_chunk_tasks()` in `file_processing.py` builds a list like `(file_path, offset, size, chunk_id)` |

```
sample_input.bin (20 MB)
├── chunk 0  (bytes 0 – 1 MB)
├── chunk 1  (bytes 1 – 2 MB)
├── chunk 2  ...
└── chunk 19 (last piece)
```

Each chunk is hashed separately; together they represent the whole file.

---

**Process** — a **separate program instance** (heavy worker)

| | |
|---|---|
| **What** | An independent Python worker with its **own memory** |
| **Library** | `multiprocessing` (`mp.Pool`, `Process`) |
| **Setting** | `num_processes` — how many processes run in parallel |
| **Default** | Number of CPU cores (`mp.cpu_count()`) |
| **Good for** | CPU-heavy work; uses **multiple cores** at once |
| **In our app** | `process_with_multiprocessing()` — each process reads and hashes different chunks |

**Analogy:** Several **separate offices**, each with its own desk and files. They don’t share the same room, but they can work on different chunks at the same time.

---

**Thread** — a **light worker inside the same program** (shared memory)

| | |
|---|---|
| **What** | A concurrent task **inside one process**, sharing the same memory |
| **Library** | `threading` (`threading.Thread`, `Semaphore`) |
| **Setting** | `num_threads` — how many threads run in parallel |
| **Default** | `4` |
| **Good for** | **I/O** (reading files from disk); threads wait on disk while others work |
| **In our app** | `process_with_multithreading()` and Sleeping Barber barbers |

**Analogy:** Several **employees in the same office**, sharing one space but doing different tasks.

---

**Process vs thread (simple comparison)**

| | Process | Thread |
|---|---------|--------|
| Memory | Separate per process | Shared in one process |
| Cost to start | Higher (~MB each) | Lower |
| True multi-core CPU | Yes (bypasses GIL) | Limited by Python GIL for CPU work |
| Our file app | `num_processes` workers hash chunks | `num_threads` workers hash chunks |
| Mode name | Multiprocessing | Multithreading / Sleeping Barber |

**Are threads inside each process?**  
**Yes.** In operating systems, a **process** is the container (program + memory). **Threads** run *inside* that process and share its memory. One process can have **one or many** threads.

```
Process (one running program)
├── Thread 1  ─┐
├── Thread 2   ├─ share same memory (same file variables, same heap)
└── Thread 3  ─┘

Process B (another program instance)  ← separate memory, cannot see Process A's variables
├── Thread 1
└── Thread 2
```

**In our project:**
- **Multithreading / Sleeping Barber:** we create **one Python process** and **`num_threads` threads inside it** (e.g. 4 barber threads in the same program).
- **Multiprocessing:** we create **`num_processes` separate processes**. Each process is its own container; Python typically runs your worker code on the **main thread of that process** (we do not spawn extra threads inside each worker in that mode).

So: threads always belong to a process; processes do not live inside threads.

**GIL (Global Interpreter Lock):** In Python, only one thread runs Python bytecode at a time **per process**. That is why **multiprocessing** is often better for heavy CPU work, and **multithreading** is still useful when threads spend time **waiting on disk I/O**.

---

**How they work together in IntegrityCheck**

We do **not** assign chunks to processes and threads at the same time. We pick **one mode** per run:

| Mode | What runs | Who gets the chunks |
|------|-----------|---------------------|
| Multiprocessing | `num_processes` **separate processes** | Each **process** gets chunks from the pool |
| Multithreading | **1 process** + `num_threads` **threads inside it** | Each **thread** gets chunks from a queue |
| Sleeping Barber | **1 process** + `num_barbers` **threads inside it** | Same idea as multithreading |

**Common confusion:** “Threads live inside a process, so how can we assign chunks to processes *or* threads?”

Answer: those are **two different ways to parallelize**, not two layers used together:

```
MODE A — Multiprocessing (num_processes = 4)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Process 1     │  │   Process 2     │  │   Process 3     │  │   Process 4     │
│  (main thread)  │  │  (main thread)  │  │  (main thread)  │  │  (main thread)  │
│  chunk 0, 4…    │  │  chunk 1, 5…    │  │  chunk 2, 6…    │  │  chunk 3, 7…    │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
     separate memory      separate memory      separate memory      separate memory

MODE B — Multithreading (num_threads = 4) — ONE process only
┌──────────────────────────────────────────────────────────────────┐
│                     Single Python process                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Thread 1 │  │ Thread 2 │  │ Thread 3 │  │ Thread 4 │         │
│  │ chunk 0  │  │ chunk 1  │  │ chunk 2  │  │ chunk 3  │  …      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
│              (all share the same memory)                          │
└──────────────────────────────────────────────────────────────────┘
```

When we say **“assign chunks to threads”**, we mean: inside **one** process, several threads pull chunks from a queue.  
When we say **“assign chunks to processes”**, we mean: several **separate** processes each handle different chunks (no extra threads in our worker code).

```
1 FILE
   ↓ split by chunk_size_kb
N CHUNKS (pieces of data)
   ↓ pick ONE mode:
   ├─→ M PROCESSES (each process handles some chunks)     ← multiprocessing
   └─→ M THREADS inside 1 process (threads share chunks)  ← multithreading / Sleeping Barber
   ↓
process_chunk() → SHA-256 per chunk
   ↓
1 full-file SHA-256 (integrity verified)
```

**Example:** 20 MB file, `chunk_size_kb=1024`, `num_threads=4`
- **20 chunks** to process
- **4 threads** take chunks from the queue and hash them
- When one thread finishes chunk 0, it picks up chunk 4, and so on

**In `ProcessingConfig`:**
- `num_processes` → used when you choose **multiprocessing** mode
- `num_threads` → used when you choose **multithreading** or **Sleeping Barber** mode
- `chunk_size_kb` → used in **all** modes (how big each piece of the file is)

**If we choose multiprocessing, do we also choose the number of threads?**  
**No — not for the parallel work.** In multiprocessing mode, only **`num_processes`** matters. The pool uses that many **processes**; `num_threads` is **ignored** by `process_with_multiprocessing()` in `file_processing.py`.

| Mode | You configure | Ignored in that mode |
|------|---------------|----------------------|
| Multiprocessing | `num_processes` | `num_threads` |
| Multithreading | `num_threads` | `num_processes` (for workers) |
| Sleeping Barber | `num_threads` (barbers) | `num_processes` (for workers) |

In `client.py` option 2, the app asks only **“Number of processes”** and sets `num_threads=4` in the config object, but that value is **not used** when hashing chunks with multiprocessing.

CLI example — only processes affect this run:
```bash
python parallel_processing.py file.bin --mode multiprocessing --num-processes 4
# --num-threads is accepted but does not change multiprocessing workers
```

Each worker **process** still has a main thread internally (that’s how OS processes work), but **we do not create extra threads** for chunk processing in this mode.

You do **not** need one process/thread per chunk. Typically you have **fewer workers than chunks**; workers reuse themselves on the next chunk until all are done.

---

#### B) Multiprocessing on real files
**File:** `file_processing.py` — class `ParallelFileProcessor`

| Setting | Constructor argument | Default |
|---------|---------------------|---------|
| Processes | `num_processes` | `mp.cpu_count()` |
| Threads | `num_threads` | `4` |

**How it works:**
1. File is split into chunks (`_chunk_tasks()`).
2. `mp.Pool(processes=self.num_processes)` runs `process_chunk` on each chunk in parallel.
3. Each process reads its chunk and computes SHA-256.

```python
with mp.Pool(processes=self.num_processes) as pool:
    chunk_results = pool.map(process_chunk, tasks)
```

#### C) Multithreading on real files
**File:** `file_processing.py` — `process_with_multithreading()`

**How it works:**
1. Chunks are put in a `queue.Queue`.
2. `self.num_threads` worker threads are created with `threading.Thread`.
3. Each thread takes a chunk, hashes it, stores result under a `threading.Lock`.

```python
threads = [
    threading.Thread(target=worker, name=f"file-worker-{index}")
    for index in range(self.num_threads)
]
```

#### D) User-facing configuration

**Interactive client** — `client.py`:
- Option 2 (multiprocessing): asks `Number of processes`
- Option 3 (multithreading): asks `Number of threads`
- Option 4 (benchmark): asks both

**CLI** — `parallel_processing.py`:
```bash
python parallel_processing.py sample_input.bin --num-processes 4 --num-threads 4 --mode benchmark
```

#### E) Helper classes (reusable pattern)
**File:** `parallel_processing.py`
- `MultiprocessingPool` — wraps `mp.Pool(num_processes)`
- `ThreadPool` — creates `num_threads` workers with a task queue

### How to demonstrate
```bash
python client.py
# Option 3 → set threads to 2 or 4
# Option 2 → set processes to 2 or 4
# Option 4 → benchmark all modes
```

### Why two approaches?
| | Multiprocessing | Multithreading |
|---|----------------|----------------|
| Library | `multiprocessing.Pool` | `threading.Thread` |
| Best for | CPU work across cores | I/O (reading file chunks) |
| GIL | Bypassed (separate processes) | Shared memory in one process |

---

## 2. Porting & Loading Existing Software Solutions

### Requirement
> Porting and loading of existing software solutions.

### What we did
- Any external `.py` file can be **loaded at runtime** without modifying our main code.
- The loader expects a function `run_solution(file_path, chunk_size_kb, num_threads)`.
- Example plugin: `sample_solution.py`.

### Libraries
```python
import importlib.util   # dynamic module loading
from pathlib import Path
```

### Where in the code

#### A) Loader class
**File:** `parallel_processing.py` — `SoftwareSolutionLoader`

```python
spec = importlib.util.spec_from_file_location(name, path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
return module
```

Then it calls:
```python
module.run_solution(file_path=..., chunk_size_kb=..., num_threads=...)
```

#### B) Example external solution
**File:** `sample_solution.py`

This file **pretends to be code written by another team** or an existing tool. It:
- Defines `run_solution(...)` 
- Processes the file with its own multithreading logic
- Returns a dict with `file_sha256`, `total_time`, etc.

#### C) How the user triggers it
**File:** `client.py` — menu option **5. Load external solution**

```python
loader = SoftwareSolutionLoader(Path(solution_path))
result = loader.run(file_path=..., chunk_size_kb=..., num_threads=...)
```

**CLI:**
```bash
python parallel_processing.py sample_input.bin --mode software --solution-path sample_solution.py
```

### Flow diagram
```
User picks sample_solution.py
        │
        ▼
SoftwareSolutionLoader.load()     ← importlib reads the file
        │
        ▼
module.run_solution(...)          ← external code runs
        │
        ▼
Returns checksum + timing         ← same interface as our app
```

### Why this matters for the course
It shows **porting**: you can plug in existing Python code without rewriting the main project — only the function signature must match.

---

## 3. Inter-Process Communication (IPC)

### Requirement
> Pipes, shared memory segments, queues.

### What we did
All three IPC techniques are implemented in **`ipc_communication.py`** as runnable demonstrations.

**Note:** IPC is **not wired into the file-processing pipeline**. It is a **separate module** that demonstrates OS concepts required by the course. The main app uses threading queues internally, but the formal IPC demos are in `ipc_communication.py`.

### Libraries
```python
from multiprocessing import Process, Pipe, Queue
import multiprocessing as mp   # Value, Array, Lock
```

### Where in the code

#### A) Pipes (one-to-one)
**File:** `ipc_communication.py` — class `PipeCommunication`

| Concept | Code |
|---------|------|
| Create pipe | `self.parent_conn, self.child_conn = Pipe()` |
| Send | `parent_conn.send(data)` |
| Receive | `child_conn.recv()` |
| Use case | Parent process talks to one child process |

**Demo:** `demonstrate_pipes()` — parent sends messages, child echoes back.

**Run:**
```bash
python ipc_communication.py
```

#### B) Queues (many-to-many)
**File:** `ipc_communication.py` — class `QueueCommunication`

| Concept | Code |
|---------|------|
| Create queue | `Queue(maxsize=10)` |
| Producer | `queue.put(item)` |
| Consumer | `queue.get(timeout=...)` |
| Use case | Multiple producer processes, multiple consumer processes |

**Demo:** `demonstrate_queues()` — 2 producers, 2 consumers.

#### C) Shared memory
**File:** `ipc_communication.py` — class `SharedMemoryData`

| Concept | Code |
|---------|------|
| Shared integer | `mp.Value('i', 0)` |
| Shared array | `mp.Array('d', [0.0] * 10)` |
| Protection | `mp.Lock()` around read/write |

**Demo:** `demonstrate_shared_memory()` — multiple processes increment the same counter safely.

### Comparison table
| IPC type | Class | Processes | Data flow |
|----------|-------|-----------|-----------|
| Pipe | `PipeCommunication` | 2 | Direct send/recv |
| Queue | `QueueCommunication` | Many | FIFO messages |
| Shared memory | `SharedMemoryData` | Many | Same memory, needs lock |

---

## 4. Synchronization — Semaphores & Classic Problems

### Requirement
> Semaphores using classic problems: dining philosophers, sleeping barber, etc.

---

## Did we use Dining Philosophers and Sleeping Barber?

| Problem | Used in project? | Where | Role in our project |
|---------|------------------|-------|---------------------|
| **Dining Philosophers** | ✅ Yes (demo only) | `synchronization.py` | Proves we understand semaphores + deadlock avoidance (not used in file processing) |
| **Sleeping Barber** | ✅ Yes (demo + real app) | `synchronization.py` + `sleeping_barber_processor.py` | Classic demo **and** applied to hash file chunks in the main app |

**Short answer for the jury:**
- **Dining Philosophers** → implemented and runnable, teaches synchronization concepts.
- **Sleeping Barber** → implemented twice: once as a classic OS demo, once as the **core algorithm** behind `client.py` option 1.

---

## What is the Dining Philosophers problem?

### The story
Five philosophers sit at a round table. Between each pair of neighbors there is **one fork** (5 forks total). To eat, a philosopher needs **both** forks — the one on their left and the one on their right.

```
        [P0]
    F4      F0
  [P4]      [P1]
    F3      F1
      [P3]-[P2]
         F2
```
(P = philosopher, F = fork)

### The problem
If every philosopher picks up their **left fork** at the same time, they all wait forever for the **right fork** → **deadlock** (nobody eats).

### The goal
Use **semaphores** (and sometimes ordering rules) so that:
- Philosophers can eat without deadlock
- No philosopher starves forever
- Multiple philosophers can eat when forks are available

### What it teaches
- **Shared resources** (forks) accessed by **multiple threads**
- **Deadlock** when everyone holds one resource and waits for another
- **Synchronization** with `Semaphore.acquire()` and `Semaphore.release()`

### Did we use it? **Yes — demonstration module**

**File:** `synchronization.py` — class `DiningPhilosophers`

| Element | Our implementation |
|---------|-------------------|
| Forks | `threading.Semaphore(1)` — one semaphore per fork |
| Philosophers | `threading.Thread` per philosopher |
| States | `THINKING` → `HUNGRY` → `EATING` |
| Protection | `threading.Lock` on shared state array |

**We did NOT** connect Dining Philosophers to file processing. It is a **standalone OS concept demo** required by the course.

**Run:**
```bash
python synchronization.py
```

---

## What is the Sleeping Barber problem?

### The story
- One **barber** cuts hair.
- There is a **waiting room** with a limited number of **chairs** (e.g. 3 or 8).
- **Customers** arrive to get a haircut.
- If the barber has no customers, he **sleeps**.
- When a customer arrives, they wake the barber.
- If all chairs are full, new customers **leave** (or wait outside in our file version).
- When the barber finishes, he serves the next customer.

```
Customers arrive  →  [Chair][Chair][Chair]  →  Barber cuts hair  →  Customer leaves
                     (waiting room)
```

### The problem
Coordinate **producer** (customers arriving) and **consumer** (barber working) with:
- A **limited buffer** (waiting chairs)
- **Sleep/wake** signalling (barber sleeps when idle)
- **Semaphores** to count customers and signal the barber

### What it teaches
- **Producer–consumer** style coordination
- **Bounded capacity** (finite waiting room)
- **Semaphores** for “something arrived” and “worker available”

### Did we use it? **Yes — twice**

#### 1) Classic demo (like the textbook)
**File:** `synchronization.py` — class `SleepingBarber`

| Semaphore | Role |
|-----------|------|
| `customers_waiting` | Signals that a customer arrived |
| `barber_available` | Signals that the barber is ready |
| `access_lock` | Protects the shared waiting-room counter |

**Run:** `python synchronization.py`

#### 2) Real application (file processing) — **this is our main use**
**File:** `sleeping_barber_processor.py` — class `SleepingBarberFileProcessor`

We mapped the barber shop onto file processing:

| Barber shop | Our file app |
|-------------|--------------|
| Customer | One **file chunk** waiting to be hashed |
| Barber | One **worker thread** |
| Chair | One slot in a **bounded queue** (`num_chairs`) |
| Shop full | Chunk cannot enter queue yet → waits |
| Barber sleeps | Thread blocks on `threading.Semaphore(0)` until a chunk arrives |
| Haircut | Compute **SHA-256** on the chunk |

**User runs it via:**
```bash
python client.py                    # Option 1
python parallel_processing.py sample_input.bin --mode sleeping_barber --num-threads 4 --num-chairs 8
```

This is the **bridge** between OS theory and our IntegrityCheck product.

---

### What we did (summary)
We use semaphores in **two places**:

1. **`synchronization.py`** — classic textbook demos (Dining Philosophers, Sleeping Barber, Producer-Consumer)
2. **`sleeping_barber_processor.py`** — Sleeping Barber **applied to real file processing** (main app)

### Library
```python
import threading
threading.Semaphore(n)   # counting semaphore (n permits)
threading.Lock()         # mutex (binary lock)
```

---

### 4A) Classic problems (demonstration module)

**File:** `synchronization.py`

All three problems below use `threading.Semaphore`. Run the whole module with:
```bash
python synchronization.py
```

#### Dining Philosophers (see explanation above)
**Class:** `DiningPhilosophers` — demo only, not in file pipeline.

#### Sleeping Barber (classic demo — see explanation above)
**Class:** `SleepingBarber` — textbook version with barber + customers.

#### Producer-Consumer
**Class:** `ProducerConsumerSemaphore`

| Semaphore | Role |
|-----------|------|
| `empty` | Free slots in buffer (initial = buffer size) |
| `full` | Filled slots (initial = 0) |

**Run:** `python synchronization.py`

---

### 4B) Sleeping Barber in the REAL application

**File:** `sleeping_barber_processor.py` — class `SleepingBarberFileProcessor`

This is where the course concept meets our file-processing app.

| Classic concept | In our file app |
|-----------------|-----------------|
| Customer | One file chunk |
| Barber | Worker `threading.Thread` |
| Chair | Slot in `queue.Queue(maxsize=num_chairs)` |
| Shop full | `queue.Full` — chunk waits |
| Barber sleeps | `threading.Semaphore(0)` — blocks until chunk arrives |

**Key code:**
```python
waiting_room = queue.Queue(maxsize=self.num_chairs)
customers_waiting = threading.Semaphore(0)

# Chunk arrives → release semaphore → barber wakes up
customers_waiting.release()

# Barber thread
customers_waiting.acquire()
chunk_task = waiting_room.get()
result = process_chunk(chunk_task)
```

**User access:**
```bash
python client.py          # Option 1
python parallel_processing.py file.bin --mode sleeping_barber --num-threads 4 --num-chairs 8
```

---

## What Is Used Where (Honest Summary)

| Requirement | In main file app? | Demo module? | Key file |
|-------------|-------------------|--------------|----------|
| Configurable multiprocessing | ✅ Yes | — | `file_processing.py` |
| Configurable multithreading | ✅ Yes | — | `file_processing.py` |
| Software solution loading | ✅ Yes | — | `parallel_processing.py`, `sample_solution.py` |
| Sleeping Barber on files | ✅ Yes | — | `sleeping_barber_processor.py` |
| Pipes | ❌ No (demo only) | ✅ Yes | `ipc_communication.py` |
| Queues (IPC) | ❌ No (demo only) | ✅ Yes | `ipc_communication.py` |
| Shared memory | ❌ No (demo only) | ✅ Yes | `ipc_communication.py` |
| Dining Philosophers | ❌ No (demo only) | ✅ Yes | `synchronization.py` |
| Sleeping Barber (classic) | ❌ No (demo only) | ✅ Yes | `synchronization.py` |
| Producer-Consumer | ❌ No (demo only) | ✅ Yes | `synchronization.py` |

For the **presentation / oral exam**, say:
- **Main product** = parallel file integrity verification (`client.py`)
- **OS concepts** = proven in dedicated modules (`ipc_communication.py`, `synchronization.py`)
- **Bridge** = Sleeping Barber applied to real chunks (`sleeping_barber_processor.py`)

---

## Quick Commands Cheat Sheet

```bash
# Main application
python client.py

# Multiprocessing
python parallel_processing.py sample_input.bin --mode multiprocessing --num-processes 4

# Multithreading
python parallel_processing.py sample_input.bin --mode multithreading --num-threads 4

# Sleeping Barber (file processing)
python parallel_processing.py sample_input.bin --mode sleeping_barber --num-threads 4 --num-chairs 8

# Load external solution
python parallel_processing.py sample_input.bin --mode software --solution-path sample_solution.py

# IPC demos
python ipc_communication.py

# Synchronization demos
python synchronization.py

# Everything together
python examples/run_all_examples.py
```

---

## One-Paragraph Answers (For Oral Exam)

**Multiprocessing / multithreading:**  
We use Python's `multiprocessing.Pool` and `threading.Thread` in `file_processing.py`. The user sets `num_processes` and `num_threads` via `client.py` or CLI flags. The file is split into chunks; each chunk is hashed in parallel.

**Software loading:**  
`SoftwareSolutionLoader` in `parallel_processing.py` uses `importlib` to load any external `.py` file that defines `run_solution()`. We demonstrate this with `sample_solution.py`.

**IPC:**  
`ipc_communication.py` implements pipes (`Pipe`), queues (`Queue`), and shared memory (`Value`, `Array`) from the `multiprocessing` module, each with a runnable demo.

**Synchronization:**  
`synchronization.py` implements Dining Philosophers, Sleeping Barber, and Producer-Consumer with `threading.Semaphore`. In the main app, we reuse the Sleeping Barber pattern in `sleeping_barber_processor.py` to process file chunks with a bounded waiting queue and barber threads.

---

*Document for course: Systèmes d'Exploitation Avancé — IntegrityCheck project*
