# Project Idea: Parallel File Integrity Verification System

## Product Name

**IntegrityCheck** — a parallel file integrity verification tool for large files.

---

## The Problem (Real-World Context)

When organizations transfer large files (backups, archives, installers, datasets), they must confirm the file arrived **complete and uncorrupted**. A single bit error can make the file unusable.

Manual verification of large files is slow. Processing the entire file on one thread does not use modern multi-core CPUs efficiently.

---

## Our Solution

A desktop client application that:

1. Lets the user select a file
2. Splits the file into configurable chunks (e.g. 1 MB each)
3. Processes chunks in parallel using OS concurrency techniques
4. Computes SHA-256 checksums per chunk and for the full file
5. Exports a JSON report with timing, throughput, and integrity results

If all processing modes produce the same checksum, the file integrity is verified.

---

## Application Domain

**Large file processing** (team choice from the course assignment).

This project processes **files only** — not video frames, not media decoding. Any binary file can be used as input (`.bin`, `.zip`, `.pdf`, `.tar`, etc.).

---

## Sleeping Barber — Applied to File Processing

The Sleeping Barber algorithm is integrated into the real application:

| Concept | Meaning in our project |
|---------|------------------------|
| Customer | One file chunk waiting to be hashed |
| Barber | One worker thread |
| Waiting chairs | Bounded queue (limited capacity) |
| Shop full | Chunk waits until a chair is free |
| Barber sleeps | Thread blocks until a chunk arrives |

This models a realistic server with **limited worker capacity** — not unlimited parallel jobs at once.

---

## Functional Needs (Besoins Fonctionnels)

| ID | Need | Implementation |
|----|------|----------------|
| BF-01 | User submits a file | `client.py` |
| BF-02 | Configurable multiprocessing | `--num-processes` |
| BF-03 | Configurable multithreading | `--num-threads` |
| BF-04 | Limited waiting queue | `SleepingBarberFileProcessor` |
| BF-05 | Benchmark all modes | Benchmark menu / CLI |
| BF-06 | Load external solution | `SoftwareSolutionLoader` |
| BF-07 | Export JSON report | `processing_report.json` |
| BF-08 | File integrity (SHA-256) | All processing modes |

---

## Technical Modules

| Module | Role |
|--------|------|
| `client.py` | End-user interactive application |
| `file_processing.py` | Core chunk processing engine |
| `sleeping_barber_processor.py` | Sleeping Barber + file chunks |
| `parallel_processing.py` | CLI, config, software loader |
| `ipc_communication.py` | Pipes, queues, shared memory (OS concepts) |
| `synchronization.py` | Semaphores, Dining Philosophers, Sleeping Barber demo |

---

## Course Requirements Coverage

| Criterion | Status |
|-----------|--------|
| High-performance parallel processing & benchmarking | Done |
| Application: large file processing | Done |
| Configurable multiprocessing & multithreading | Done |
| Porting/loading existing software solutions | Done |
| IPC: pipes, queues, shared memory | Done |
| Synchronization: semaphores + classic problems | Done |
| Source code + technical specifications | Done |
| Demo video | Team deliverable |
| Presentation | Team deliverable |

---

## How to Run (Demo)

```bash
cd parallel_processing_project

# Interactive client
python client.py

# Sleeping Barber mode from CLI
python parallel_processing.py sample_input.bin --create-sample --mode sleeping_barber

# Full benchmark
python parallel_processing.py sample_input.bin --mode benchmark --output-report processing_report.json
```

---

## Example User Story

> An IT administrator receives a 20 MB backup archive after a server migration.  
> They open **IntegrityCheck**, select the file, and run Sleeping Barber mode with 4 barbers and 8 chairs.  
> The tool processes all chunks in parallel, prints progress, and outputs the SHA-256 checksum.  
> The JSON report is saved for the audit log. File verified.

---

## Team

**Course:** Systèmes d'Exploitation Avancé (Advanced Operating Systems)  
**Year:** 2026
