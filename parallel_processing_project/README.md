# Parallel File Processing & Benchmarking Project

## Project Summary

This Python project demonstrates **high-performance parallel file processing, inter-process communication, synchronization, and benchmarking** for the "Systèmes d'Exploitation Avancé" (Advanced Operating Systems) course.

**Application domain:** Large file processing (team choice)  
**Status:** Complete — all requirements implemented and tested

---

## Quick Links

- **Project Idea:** [PROJECT_IDEA.md](PROJECT_IDEA.md)
- **Technical Guide (how we implemented each requirement):** [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)
- **Get Started:** [INSTRUCTIONS.md](INSTRUCTIONS.md)
- **Technical Specs:** [REQUIREMENTS.md](REQUIREMENTS.md)
- **Interactive Client:** `python client.py`
- **Quick Demo:** `python quick_start.py`
- **Full Suite:** `python examples/run_all_examples.py`

---

## What's Included

### 1. **Parallel File Processing** (main application)
- Reads real files in configurable chunks
- Computes SHA-256 checksums per chunk and for the full file
- **Sequential**, **multiprocessing**, and **multithreading** execution modes
- Configurable number of processes and threads
- JSON benchmark reports (`processing_report.json`)

### 2. **Interprocess Communication (IPC)**
- **Pipes:** One-to-one process communication
- **Queues:** Multi-producer/consumer message passing
- **Shared Memory:** Direct memory sharing with synchronization

### 3. **Synchronization Primitives**
- **Semaphores:** Resource counting and control
- **Locks/Mutexes:** Critical section protection

### 4. **Classic Synchronization Problems**
- **Dining Philosophers:** Deadlock-free resource allocation
- **Sleeping Barber:** Producer-consumer with constraints
- **Producer-Consumer:** Bounded buffer synchronization

### 5. **Software Solution Loading**
- Dynamic import of external Python modules (`sample_solution.py`)
- Pluggable file-processing implementations via `SoftwareSolutionLoader`

### 6. **Benchmarking & Performance Analysis**
- Sequential vs multiprocessing vs multithreading comparisons
- Speedup calculations
- Throughput metrics (MB/s)
- Checksum verification across all methods

---

## Functional Needs (Besoins Fonctionnels)

| ID | Need | Implementation |
|----|------|----------------|
| BF-01 | User submits a file for processing | `client.py` interactive menu |
| BF-02 | Configurable multiprocessing | `--num-processes` / menu option 2 |
| BF-03 | Configurable multithreading | `--num-threads` / menu option 3 |
| BF-04 | Limited waiting queue (Sleeping Barber) | `SleepingBarberFileProcessor` / menu option 1 |
| BF-05 | Compare all modes + benchmarking | menu option 4 / `--mode benchmark` |
| BF-06 | Load external software solution | menu option 5 / `--mode software` |
| BF-07 | Export JSON processing report | `processing_report.json` |
| BF-08 | File integrity check (SHA-256) | all processing modes |

### Sleeping Barber mapping
- **Customer** = file chunk waiting to be hashed
- **Barber** = worker thread
- **Chairs** = bounded waiting queue (`num_chairs`)
- **Shop full** = chunk waits until a chair is free

---

## Quick Start

### Interactive client (recommended for end users)
```bash
cd parallel_processing_project
python client.py
```

### Process a file from command line
```bash
python parallel_processing.py sample_input.bin --create-sample --sample-size-mb 20 --mode sleeping_barber
```

### Quick overview (30 seconds)
```bash
python quick_start.py
```

### Full suite (IPC + sync + file processing)
```bash
python examples/run_all_examples.py
```

### Individual modules
```bash
# File processing CLI
python parallel_processing.py sample_input.bin --mode benchmark

# Alternative file processing entry point
python examples/real_world_examples.py sample_input.bin --mode benchmark

# IPC demonstrations
python ipc_communication.py

# Synchronization demonstrations
python synchronization.py
```

---

## Project Structure

```
parallel_processing_project/
│
├── README.md                       ← You are here
├── REQUIREMENTS.md                 ← Technical specification
├── INSTRUCTIONS.md               ← How to run everything
│
├── client.py                       ← Interactive user application
├── file_processing.py              ← Core file processing engine
├── sleeping_barber_processor.py    ← Sleeping Barber + file processing
├── parallel_processing.py          ← CLI + configurable processor
├── sample_solution.py              ← External solution (loaded at runtime)
├── sample_input.bin                ← Sample binary file for testing
├── processing_report.json          ← Generated benchmark report
│
├── ipc_communication.py            ← Pipes, Queues, Shared Memory
├── synchronization.py              ← Semaphores & classic problems
├── quick_start.py                  ← Quick demo
│
└── examples/
    ├── run_all_examples.py         ← Master runner
    └── real_world_examples.py      ← File processing CLI
```

---

## Key Features

### File Processing
- **Chunk-based I/O:** Configurable chunk size (default 1 MB)
- **SHA-256 integrity:** Per-chunk and full-file checksums
- **Three execution modes:** Sequential, multiprocessing, multithreading
- **JSON reports:** Timing, throughput, and per-chunk results

### Multiprocessing & Multithreading
- **Configurable processes:** Default = CPU count
- **Configurable threads:** Default = 4
- **Benchmarking:** Compare all three modes on the same file

### IPC Techniques
- **Pipes:** Low-overhead 1-to-1 communication
- **Queues:** Thread/process-safe multi-producer/consumer
- **Shared Memory:** High-performance memory sharing with protection

### Synchronization
- **Semaphores:** Binary and counting
- **Classic problems:** Dining Philosophers, Sleeping Barber, Producer-Consumer

---

## Sample Output

### File Processing Benchmark
```
============================================================
FILE PROCESSING BENCHMARK
============================================================
File: sample_input.bin
Size: 20.00 MB
Chunk size: 512 KB
Chunks: 40
Processes: 4
Threads: 4

Sequential:
  Time: 0.05 s
  Throughput: 367.30 MB/s
  File SHA-256: aef406dbd745899858bb713fd5b137c50fb9dc9c85576b99a82af66989509bc5

Multiprocessing:
  Time: 0.21 s
  Throughput: 94.96 MB/s
  File SHA-256: aef406dbd745899858bb713fd5b137c50fb9dc9c85576b99a82af66989509bc5

Multithreading:
  Time: 0.03 s
  Throughput: 597.00 MB/s
  File SHA-256: aef406dbd745899858bb713fd5b137c50fb9dc9c85576b99a82af66989509bc5

Checksums match across all methods: True
Multiprocessing speedup: 0.26x
Multithreading speedup: 1.63x
```

---

## CLI Options

```bash
python parallel_processing.py <file_path> [options]

Options:
  --mode {sequential,multiprocessing,multithreading,sleeping_barber,benchmark,software}
  --num-chairs N             # Waiting chairs for Sleeping Barber (default: 8)
  --num-processes N          # Worker processes (default: CPU count)
  --num-threads N            # Worker threads (default: 4)
  --chunk-size-kb N          # Chunk size in KB (default: 1024)
  --create-sample            # Create sample file if missing
  --sample-size-mb N         # Sample file size (default: 10)
  --output-report PATH       # Save JSON benchmark report
  --solution-path PATH       # External solution module (software mode)
```

---

## System Requirements

- **Python:** 3.8 or higher
- **OS:** Windows, Linux, macOS
- **Dependencies:** None (standard library only)
- **Cores:** 2+ recommended for meaningful benchmarks

---

## Files Overview

| File | Purpose | Status |
|------|---------|--------|
| `file_processing.py` | Core engine: chunk I/O, SHA-256, benchmarking | Done |
| `parallel_processing.py` | CLI, config, software loader | Done |
| `ipc_communication.py` | Pipes, Queues, Shared Memory | Done |
| `synchronization.py` | Semaphores & classic problems | Done |
| `examples/real_world_examples.py` | File processing CLI | Done |
| `examples/run_all_examples.py` | Master example runner | Done |
| `sample_solution.py` | External pluggable solution | Done |
| `quick_start.py` | Quick demo | Done |
| `REQUIREMENTS.md` | Technical specification | Done |

---

## Course Requirements Coverage

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Application domain (file processing) | `ParallelFileProcessor` | Done |
| Multiprocessing | `process_with_multiprocessing()` | Done |
| Multithreading | `process_with_multithreading()` | Done |
| Configurable processes | `ProcessingConfig.num_processes` | Done |
| Configurable threads | `ProcessingConfig.num_threads` | Done |
| Software solution loading | `SoftwareSolutionLoader` | Done |
| Pipes IPC | `PipeCommunication` | Done |
| Queues IPC | `QueueCommunication` | Done |
| Shared Memory IPC | `SharedMemoryData` | Done |
| Semaphores | Synchronization classes | Done |
| Dining Philosophers | `DiningPhilosophers` | Done |
| Sleeping Barber (demo) | `SleepingBarber` in `synchronization.py` | Done |
| Sleeping Barber (file processing) | `SleepingBarberFileProcessor` | Done |
| User client application | `client.py` | Done |
| Benchmarking | `benchmark()` + JSON reports | Done |
| English comments | All source files | Done |

---

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Source code | This repository |
| Technical specifications | [REQUIREMENTS.md](REQUIREMENTS.md) |
| Demo video | To be recorded by the team |
| Presentation | To be prepared by the team |

---

## References

- [Python multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [Python hashlib](https://docs.python.org/3/library/hashlib.html)

---

## License

MIT License — free to use for educational purposes

---

**Ready to run:**
```bash
python parallel_processing.py sample_input.bin --create-sample --mode benchmark
```
