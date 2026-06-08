# TECHNICAL REQUIREMENTS & SPECIFICATION

## Project Overview

**Title:** Parallel File Processing & Benchmarking System

**Domain:** Large File Processing (team choice)

**Language:** Python 3.8+

**Duration:** Single-session execution (configurable file size and chunk size)

**Status:** Complete

---

## Project Context

High-performance parallel processing and benchmarking applied to **large file processing**:

- Read files in configurable chunks
- Compute SHA-256 checksums per chunk and for the full file
- Compare sequential, multiprocessing, multithreading, and Sleeping Barber performance
- Demonstrate OS concepts: IPC, synchronization, and classic concurrency problems
- Provide a simple **client application** for end-user interaction

---

## Functional Needs (Besoins Fonctionnels)

| ID | Besoin | Description | Module |
|----|--------|-------------|--------|
| BF-01 | Soumettre un fichier | L'utilisateur choisit un fichier à traiter | `client.py` |
| BF-02 | Multiprocessing configurable | Nombre de processus ajustable | `parallel_processing.py` |
| BF-03 | Multithreading configurable | Nombre de threads ajustable | `parallel_processing.py` |
| BF-04 | File d'attente limitée | Sleeping Barber appliqué aux chunks | `sleeping_barber_processor.py` |
| BF-05 | Benchmarking | Comparer tous les modes de traitement | `client.py` option 4 |
| BF-06 | Charger solution externe | Import dynamique d'un module Python | `SoftwareSolutionLoader` |
| BF-07 | Rapport JSON | Exporter temps, débit, checksums | `processing_report.json` |
| BF-08 | Vérification d'intégrité | SHA-256 fichier + chunks | `file_processing.py` |

### Sleeping Barber applied to file processing

| Concept | File processing meaning |
|---------|-------------------------|
| Customer | One file chunk to hash |
| Barber | One worker thread |
| Waiting chairs | Bounded queue (`num_chairs`) |
| Shop full | Chunk waits outside until a chair is free |
| Barber sleeps | Thread blocks on `customers_waiting` semaphore |

---

## Functional Requirements

### 1. Multiprocessing & Multithreading (CONFIGURABLE)

#### 1.1 Process Configuration
```
Variable number of processes
Default: CPU count (cpu_count())
Min: 1, Max: limited by system resources
Application: parallel chunk hashing via multiprocessing
```

**Implementation:**
- `ProcessingConfig.num_processes`
- `ParallelFileProcessor.process_with_multiprocessing()`
- `mp.Pool(processes=num_processes)`

#### 1.2 Thread Configuration
```
Variable number of threads
Default: 4 threads
Min: 1, Max: configurable
Application: parallel chunk I/O and hashing via multithreading
```

**Implementation:**
- `ProcessingConfig.num_threads`
- `ParallelFileProcessor.process_with_multithreading()`
- Worker threads with shared task queue and result lock

---

### 2. Porting and Loading of Existing Software Solutions

```
Dynamically load external Python modules at runtime
External module must expose run_solution(file_path, chunk_size_kb, num_threads)
```

**Implementation:**
- `SoftwareSolutionLoader` in `parallel_processing.py`
- `sample_solution.py` as reference external solution
- Loaded via `importlib.util`

**Usage:**
```bash
python parallel_processing.py sample_input.bin --mode software --solution-path sample_solution.py
```

---

### 3. Interprocess Communication (IPC) — REQUIRED

#### 3.1 Pipes (One-to-One)
- **Class:** `PipeCommunication` in `ipc_communication.py`
- Bidirectional parent-child communication
- Demonstrated independently of file processing

#### 3.2 Queues (Multi-to-Multi)
- **Class:** `QueueCommunication` in `ipc_communication.py`
- Thread-safe and process-safe FIFO messaging
- Multiple producers and consumers

#### 3.3 Shared Memory (Direct Access)
- **Class:** `SharedMemoryData` in `ipc_communication.py`
- Shared integers and arrays protected by locks
- Atomic counter and array updates

---

### 4. Synchronization — REQUIRED

#### 4.1 Semaphores
- Binary and counting semaphores via `threading.Semaphore`
- Used in all classic problem implementations

#### 4.2 Locks/Mutexes
- `threading.Lock` for critical sections
- Used in shared memory and multithreaded file result collection

#### 4.3 Classic Problems

| Problem | Class | File |
|---------|-------|------|
| Dining Philosophers | `DiningPhilosophers` | `synchronization.py` |
| Sleeping Barber | `SleepingBarber` | `synchronization.py` |
| Producer-Consumer | `ProducerConsumerSemaphore` | `synchronization.py` |

---

### 5. Sleeping Barber in File Processing — REQUIRED

- **Module:** `sleeping_barber_processor.py`
- **Class:** `SleepingBarberFileProcessor`
- **Method:** `process_with_sleeping_barber()`

**Synchronization used:**
- `threading.Semaphore(0)` — signals barbers when a chunk arrives
- `queue.Queue(maxsize=num_chairs)` — bounded waiting room
- `threading.Lock` — protects shared results list

**User interaction:**
```bash
python client.py          # menu option 1
python parallel_processing.py file.bin --mode sleeping_barber --num-threads 4 --num-chairs 8
```

---

### 6. File Processing Application — REQUIRED

#### 5.1 Core Engine
- **Module:** `file_processing.py`
- **Class:** `ParallelFileProcessor`

**Operations:**
| Method | Description |
|--------|-------------|
| `process_sequential()` | Single-threaded chunk read and hash |
| `process_with_multiprocessing()` | Parallel chunk processing with process pool |
| `process_with_multithreading()` | Parallel chunk processing with worker threads |
| `benchmark()` | Run all three modes and compare results |
| `save_report()` | Export JSON report with metrics and per-chunk hashes |

#### 5.2 Processing Pipeline
```
Input file
    │
    ▼
Split into chunks (configurable size, default 1 MB)
    │
    ├── Sequential: read and hash chunks one by one
    ├── Multiprocessing: distribute chunks across processes
    └── Multithreading: distribute chunks across threads
    │
    ▼
Per-chunk SHA-256 + full-file SHA-256 verification
    │
    ▼
Benchmark metrics + optional JSON report
```

#### 5.3 Data Integrity
- All three execution modes must produce the **same full-file SHA-256**
- Per-chunk checksums recorded in benchmark output
- Checksum match verified automatically in `benchmark()`

---

### 7. Client Application — REQUIRED

- **Module:** `client.py`
- Interactive menu for end users
- Options: Sleeping Barber, multiprocessing, multithreading, benchmark, external solution

---

### 8. Benchmarking & Performance Analysis

#### 6.1 Metrics Collected
```
Total execution time (seconds)
Throughput (MB/s)
Chunks processed
Number of workers (processes or threads)
Per-chunk SHA-256 and execution time
Full-file SHA-256
Speedup = Sequential_Time / Parallel_Time
```

#### 6.2 Output Formats
- Console benchmark summary
- JSON report file (`processing_report.json`)

#### 6.3 Example Results (20 MB file, 512 KB chunks, 4 workers)
```
Sequential:      ~0.05 s,  ~367 MB/s
Multiprocessing: ~0.21 s,   ~95 MB/s  (process overhead on I/O-bound work)
Multithreading:  ~0.03 s,  ~597 MB/s  (best for file I/O on this workload)
Checksums match: True
```

*Actual results depend on CPU, disk speed, file size, and chunk size.*

---

## Non-Functional Requirements

### Code Quality
- English comments throughout
- Docstrings on all classes and public methods
- Modular design with separate concerns
- Error handling for missing files and invalid paths

### Documentation
- `README.md` — project overview
- `REQUIREMENTS.md` — this technical specification
- `INSTRUCTIONS.md` — how to run
- Inline code documentation

### Testing
- All modules runnable as standalone scripts
- `run_all_examples.py` runs the full demonstration suite
- Real file used for benchmarks (`sample_input.bin`)

### Maintainability
- No external dependencies (stdlib only)
- Python 3.8+ compatible
- Cross-platform (Windows, Linux, macOS)

---

## Module Structure

```
parallel_processing_project/
│
├── file_processing.py
│   ├── ChunkResult                    [Dataclass]
│   ├── FileProcessingResult           [Dataclass]
│   ├── process_chunk()                  [Function]
│   ├── ParallelFileProcessor            [Class]
│   └── create_sample_file()             [Function]
│
├── client.py
│   └── main()                           [Interactive user menu]
│
├── parallel_processing.py
│   ├── ProcessingConfig                 [Dataclass]
│   ├── ConfigurableParallelProcessor    [Class]
│   ├── SoftwareSolutionLoader           [Class]
│   └── CLI entry point                  [main()]
│
├── sleeping_barber_processor.py
│   └── SleepingBarberFileProcessor      [Class]
│
├── ipc_communication.py
│   ├── PipeCommunication                [Class]
│   ├── QueueCommunication               [Class]
│   └── SharedMemoryData                 [Class]
│
├── synchronization.py
│   ├── DiningPhilosophers               [Class]
│   ├── SleepingBarber                   [Class]
│   └── ProducerConsumerSemaphore        [Class]
│
├── sample_solution.py
│   └── run_solution()                   [Function — external plugin]
│
└── examples/
    ├── real_world_examples.py           [File processing CLI]
    └── run_all_examples.py              [Full demo runner]
```

---

## Execution Flow

### Interactive client (end user)
```bash
python client.py
```

### Main file processing (CLI)
```bash
python parallel_processing.py sample_input.bin --create-sample --mode sleeping_barber
```

```
1. Load or create input file
2. Split file into chunks
3. Run sequential processing
4. Run multiprocessing
5. Run multithreading
6. Verify checksums match
7. Print speedup and throughput
8. Optionally save processing_report.json
```

### Full demonstration suite
```bash
python examples/run_all_examples.py
```

```
PART 1: IPC (Pipes → Queues → Shared Memory)
PART 2: Synchronization (Dining Philosophers → Sleeping Barber → Producer-Consumer)
PART 3: File Processing (Multiprocessing → Multithreading → Sleeping Barber → Benchmark → Software Loading)
PART 4: JSON Report Generation
```

---

## Configuration Parameters

```python
# ProcessingConfig / CLI flags
num_processes = cpu_count()   # --num-processes
num_threads = 4               # --num-threads
chunk_size_kb = 1024          # --chunk-size-kb
file_path = "sample_input.bin"

# Sample file generation
sample_size_mb = 10           # --sample-size-mb
```

---

## Exit Criteria & Verification

### Multiprocessing & Multithreading
- [x] Variable process count
- [x] Variable thread count
- [x] Configurable via `ProcessingConfig` and CLI

### Software Solution Loading
- [x] Dynamic module import
- [x] External `run_solution()` interface
- [x] Demonstrated with `sample_solution.py`

### Interprocess Communication
- [x] Pipes implemented and demonstrated
- [x] Queues implemented and demonstrated
- [x] Shared memory implemented and demonstrated

### Synchronization
- [x] Semaphores (binary and counting)
- [x] Locks for critical sections
- [x] Dining Philosophers working
- [x] Sleeping Barber working
- [x] Producer-Consumer working

### File Processing Application
- [x] Real file chunk-based processing
- [x] SHA-256 per chunk and full file
- [x] Sequential, multiprocessing, and multithreading modes
- [x] Benchmarking with speedup and throughput
- [x] JSON report output

### Documentation & Deliverables
- [x] Source code
- [x] Technical specification (this document)
- [x] Project idea description (`PROJECT_IDEA.md`)
- [x] Presentation (`presentation.pptx`)
- [ ] Git link (team submission)
- [ ] Demo video (team submission)

---

## Expected Output Samples

### File Processing Benchmark
```
FILE PROCESSING BENCHMARK
File: sample_input.bin
Size: 20.00 MB
Chunks: 40

Sequential:
  Time: 0.05 s
  Throughput: 367.30 MB/s
  File SHA-256: aef406db...

Multithreading:
  Time: 0.03 s
  Throughput: 597.00 MB/s
  File SHA-256: aef406db...

Checksums match across all methods: True
Multithreading speedup: 1.63x
```

### Dining Philosophers
```
Philosopher 0: Thinking...
Philosopher 0: Hungry, trying to get forks...
Philosopher 0: Eating! (cycle 1)
```

---

## Compliance Summary

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Application: file processing | Done | `file_processing.py` |
| Multiprocessing | Done | `process_with_multiprocessing()` |
| Multithreading | Done | `process_with_multithreading()` |
| Configurable processes | Done | `ProcessingConfig.num_processes` |
| Configurable threads | Done | `ProcessingConfig.num_threads` |
| Software solution loading | Done | `SoftwareSolutionLoader` |
| Pipes IPC | Done | `ipc_communication.py` |
| Queues IPC | Done | `ipc_communication.py` |
| Shared Memory IPC | Done | `ipc_communication.py` |
| Semaphores | Done | `synchronization.py` |
| Dining Philosophers | Done | `synchronization.py` |
| Sleeping Barber (theory demo) | Done | `synchronization.py` |
| Sleeping Barber (file processing) | Done | `sleeping_barber_processor.py` |
| Client application | Done | `client.py` |
| Benchmarking | Done | `benchmark()`, `processing_report.json` |
| English comments | Done | All source files |
| Runnable examples | Done | `examples/`, CLI scripts |

**All implementation requirements: MET**

---

## Version Information

- **Python Version:** 3.8+
- **Platform:** Windows, Linux, macOS
- **Dependencies:** None (standard library only)
- **Last Updated:** June 2026
- **Status:** Ready for evaluation

---

**Document End**
