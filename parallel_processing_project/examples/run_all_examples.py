"""
Main Example Runner
Demonstrates all parallel processing concepts in one place.
Run this file to see all examples together.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ipc_communication import demonstrate_pipes, demonstrate_queues, demonstrate_shared_memory
from synchronization import (
    demonstrate_dining_philosophers,
    demonstrate_sleeping_barber,
    demonstrate_producer_consumer
)
from parallel_processing import (
    ProcessingConfig,
    demonstrate_multiprocessing,
    demonstrate_multithreading,
    demonstrate_benchmarking,
    demonstrate_software_loading
)
from examples.real_world_examples import FileProcessor, create_sample_file


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f" {title}".center(70))
    print("="*70 + "\n")


def run_all_examples():
    """Run all parallel processing examples"""
    
    print_header("PARALLEL PROCESSING & BENCHMARKING PROJECT")
    print("Intensive parallel processing with configurable threads/processes\n")
    
    # =========================================================================
    # PART 1: INTERPROCESS COMMUNICATION (IPC)
    # =========================================================================
    print_header("PART 1: INTERPROCESS COMMUNICATION (IPC)")
    print("Demonstrates: Pipes, Queues, Shared Memory Segments\n")
    
    try:
        print("1.1 - Pipe Communication Demo")
        print("-" * 70)
        demonstrate_pipes()
        print("\n✓ Pipes demonstration completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Pipes demo failed: {e}\n")
    
    try:
        print("1.2 - Queue Communication Demo")
        print("-" * 70)
        demonstrate_queues()
        print("\n✓ Queues demonstration completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Queues demo failed: {e}\n")
    
    try:
        print("1.3 - Shared Memory Demo")
        print("-" * 70)
        demonstrate_shared_memory()
        print("\n✓ Shared memory demonstration completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Shared memory demo failed: {e}\n")
    
    # =========================================================================
    # PART 2: SYNCHRONIZATION & CLASSIC PROBLEMS
    # =========================================================================
    print_header("PART 2: SYNCHRONIZATION WITH SEMAPHORES")
    print("Demonstrates: Semaphores, Locks, Classic Synchronization Problems\n")
    
    try:
        print("2.1 - Dining Philosophers Problem")
        print("-" * 70)
        demonstrate_dining_philosophers()
        print("\n✓ Dining Philosophers completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Dining Philosophers demo failed: {e}\n")
    
    try:
        print("2.2 - Sleeping Barber Problem")
        print("-" * 70)
        demonstrate_sleeping_barber()
        print("\n✓ Sleeping Barber completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Sleeping Barber demo failed: {e}\n")
    
    try:
        print("2.3 - Producer-Consumer Problem")
        print("-" * 70)
        demonstrate_producer_consumer()
        print("\n✓ Producer-Consumer completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Producer-Consumer demo failed: {e}\n")
    
    # =========================================================================
    # PART 3: MULTIPROCESSING & MULTITHREADING
    # =========================================================================
    print_header("PART 3: CONFIGURABLE PARALLEL PROCESSING")
    print("Demonstrates: Multiprocessing, Multithreading, Benchmarking\n")
    
    try:
        print("3.1 - Multiprocessing Demo (CPU-bound tasks)")
        print("-" * 70)
        demonstrate_multiprocessing()
        print("\n✓ Multiprocessing demonstration completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Multiprocessing demo failed: {e}\n")
    
    try:
        print("3.2 - Multithreading Demo (I/O-bound tasks)")
        print("-" * 70)
        demonstrate_multithreading()
        print("\n✓ Multithreading demonstration completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Multithreading demo failed: {e}\n")
    
    try:
        print("3.3 - Benchmarking Demo (Sequential vs Parallel)")
        print("-" * 70)
        demonstrate_benchmarking(ProcessingConfig(
            num_processes=4,
            num_threads=4,
            workload_size=100
        ), num_tasks=4)
        print("\n✓ Benchmarking demonstration completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Benchmarking demo failed: {e}\n")
    
    try:
        print("3.4 - Software Loading Demo")
        print("-" * 70)
        demonstrate_software_loading("sample_solution.py", num_tasks=4, workload_size=100)
        print("\n✓ Software loading demonstration completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Software loading demo failed: {e}\n")
    
    # =========================================================================
    # PART 4: REAL-WORLD EXAMPLES
    # =========================================================================
    print_header("PART 4: REAL-WORLD PARALLEL PROCESSING")
    print("Demonstrates: Real file processing\n")
    
    try:
        print("4.1 - Real File Processing Example")
        print("-" * 70)
        from multiprocessing import cpu_count
        sample_file = Path("sample_input.bin")
        create_sample_file(sample_file, size_mb=10)
        file_proc = FileProcessor(file_path=sample_file, chunk_size_kb=1024, num_workers=cpu_count())
        file_proc.benchmark()
        print("\n✓ Real file processing example completed successfully\n")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Real file processing demo failed: {e}\n")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_header("PROJECT SUMMARY")
    print("""
KEY CONCEPTS DEMONSTRATED:

1. INTERPROCESS COMMUNICATION (IPC)
   ✓ Pipes: One-to-one communication between processes
   ✓ Queues: Multi-producer/consumer message passing
   ✓ Shared Memory: Direct memory sharing between processes

2. SYNCHRONIZATION
   ✓ Semaphores: Control access to shared resources
   ✓ Locks: Mutual exclusion
   ✓ Condition Variables: Wait-notify patterns

3. CLASSIC PROBLEMS SOLVED
   ✓ Dining Philosophers: Deadlock avoidance
   ✓ Sleeping Barber: Resource management
   ✓ Producer-Consumer: Buffer synchronization

4. PARALLEL PROCESSING
   ✓ Multiprocessing: True parallelism for CPU-bound tasks
   ✓ Multithreading: Shared memory concurrency for I/O-bound tasks
   ✓ Benchmarking: Measuring performance improvements

5. REAL-WORLD APPLICATIONS
   ✓ Video/Media Processing: Parallel frame processing
   ✓ File Processing: Chunk-based parallel I/O
   ✓ Configurable parallelism: Adapt to hardware capabilities

PERFORMANCE INSIGHTS:
   - Multiprocessing: Best for CPU-intensive work (GIL bypass)
   - Multithreading: Better for I/O-intensive work
   - Always benchmark before choosing approach
   - Speedup depends on: task type, system resources, synchronization overhead

PROJECT STRUCTURE:
   ├── ipc_communication.py      (Pipes, Queues, Shared Memory)
   ├── synchronization.py         (Semaphores, Classic Problems)
   ├── parallel_processing.py     (Multiprocessing/Threading)
   └── examples/
       └── real_world_examples.py (Video, File Processing)
""")
    
    print("="*70)
    print(" Project Completed Successfully!")
    print("="*70)


if __name__ == "__main__":
    run_all_examples()
