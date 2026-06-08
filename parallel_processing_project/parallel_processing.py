"""
Multiprocessing and Multithreading Utilities Module
Demonstrates configurable processes and threads with benchmarking.
"""

import argparse
import importlib.util
import queue
import multiprocessing as mp
import threading
import time
import os
from pathlib import Path
from typing import Callable, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ProcessingConfig:
    """Configuration for parallel processing"""
    num_processes: int  # Number of processes
    num_threads: int    # Number of threads
    workload_size: int  # Size of workload per worker


class MultiprocessingPool:
    """
    Pool of worker processes for parallel processing.
    Distributes work across configurable number of processes.
    """
    
    def __init__(self, num_processes: int = None):
        """
        Initialize process pool.
        
        Args:
            num_processes: Number of processes (None = CPU count)
        """
        if num_processes is None:
            num_processes = mp.cpu_count()
        
        self.num_processes = num_processes
        self.pool = mp.Pool(processes=num_processes)
    
    def map_work(self, func: Callable, items: List[Any]) -> List[Any]:
        """
        Map function across items using process pool.
        
        Args:
            func: Function to apply
            items: Items to process
            
        Returns:
            Results from all processes
        """
        return self.pool.map(func, items)
    
    def close(self):
        """Close the pool"""
        self.pool.close()
        self.pool.join()


class ThreadPool:
    """
    Pool of worker threads for parallel processing.
    Distributes work across configurable number of threads.
    """
    
    def __init__(self, num_threads: int = 4):
        """
        Initialize thread pool.
        
        Args:
            num_threads: Number of worker threads
        """
        self.num_threads = num_threads
        self.threads = []
        self.task_queue = queue.Queue()
        self.results = []
        self.results_lock = threading.Lock()
    
    def worker_thread(self, thread_id: int):
        """
        Worker thread that processes tasks.
        
        Args:
            thread_id: Thread identifier
        """
        processed_count = 0
        
        while True:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:  # Sentinel value to stop
                    break
                func, args, kwargs = task
                result = func(*args, **kwargs)
                
                with self.results_lock:
                    self.results.append(result)
                
                processed_count += 1
            except queue.Empty:
                break
            except Exception:
                break
        
        print(f"Thread {thread_id}: Processed {processed_count} tasks")
    
    def submit_task(self, func: Callable, *args, **kwargs):
        """
        Submit a task to the thread pool.
        
        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
        """
        self.task_queue.put((func, args, kwargs))
    
    def start_workers(self):
        """Start worker threads"""
        self.task_queue = queue.Queue()
        self.results = []
        self.threads = []
        
        for i in range(self.num_threads):
            t = threading.Thread(target=self.worker_thread, args=(i,))
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def wait_completion(self):
        """Wait for all tasks to complete"""
        for _ in range(self.num_threads):
            self.task_queue.put(None)
        for t in self.threads:
            t.join()
        return self.results


class SoftwareSolutionLoader:
    """Dynamically load and run an existing Python software solution."""

    def __init__(self, solution_path: Path):
        self.solution_path = Path(solution_path)
        if not self.solution_path.exists():
            raise FileNotFoundError(f"Solution file not found: {self.solution_path}")

    def load(self):
        spec = importlib.util.spec_from_file_location(
            self.solution_path.stem,
            str(self.solution_path)
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {self.solution_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run(self, num_tasks: int = 4, workload_size: int = 100):
        module = self.load()
        if hasattr(module, 'run_solution'):
            return module.run_solution(num_tasks=num_tasks, workload_size_kb=workload_size)
        raise AttributeError(
            "Loaded module must define run_solution(num_tasks, workload_size_kb)"
        )


class ConfigurableParallelProcessor:
    """
    Flexible parallel processor with configurable processes and threads.
    """
    
    def __init__(self, config: ProcessingConfig):
        """
        Initialize processor.
        
        Args:
            config: Processing configuration
        """
        self.config = config
        self.results = []
        self.execution_time = 0
    
    def cpu_bound_task(self, task_id: int) -> dict:
        """
        CPU-bound task: compute Fibonacci.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task result dictionary
        """
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        
        start = time.time()
        
        # Compute fibonacci
        result = fibonacci(30)
        
        elapsed = time.time() - start
        
        return {
            'task_id': task_id,
            'process_id': os.getpid(),
            'thread_id': threading.current_thread().ident,
            'result': result,
            'execution_time': elapsed
        }
    
    def io_bound_task(self, task_id: int) -> dict:
        """
        I/O-bound task: simulate file processing.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task result dictionary
        """
        start = time.time()
        
        # Simulate I/O operation
        time.sleep(0.1)
        
        # Process data
        data_size = self.config.workload_size
        processed_bytes = data_size * 1024  # Convert KB to bytes
        
        elapsed = time.time() - start
        
        return {
            'task_id': task_id,
            'process_id': os.getpid(),
            'thread_id': threading.current_thread().ident,
            'bytes_processed': processed_bytes,
            'execution_time': elapsed
        }
    
    def process_with_multiprocessing(self, num_tasks: int) -> dict:
        """
        Process tasks using multiprocessing.
        
        Args:
            num_tasks: Number of tasks to process
            
        Returns:
            Benchmark results
        """
        start = time.time()
        
        # Use process pool
        pool = mp.Pool(processes=self.config.num_processes)
        
        # Create tasks
        tasks = list(range(num_tasks))
        
        # Execute in parallel
        results = pool.map(self.cpu_bound_task, tasks)
        
        pool.close()
        pool.join()
        
        total_time = time.time() - start
        
        return {
            'method': 'multiprocessing',
            'num_processes': self.config.num_processes,
            'total_time': total_time,
            'tasks': num_tasks,
            'results': results
        }
    
    def process_with_threading(self, num_tasks: int) -> dict:
        """
        Process tasks using multithreading.
        
        Args:
            num_tasks: Number of tasks to process
            
        Returns:
            Benchmark results
        """
        start = time.time()
        
        results = []
        results_lock = threading.Lock()
        task_queue = list(range(num_tasks))
        queue_lock = threading.Lock()
        
        def worker():
            while True:
                with queue_lock:
                    if not task_queue:
                        return
                    task_id = task_queue.pop(0)

                result = self.io_bound_task(task_id)
                with results_lock:
                    results.append(result)
        
        # Create and start threads
        threads = []
        for i in range(self.config.num_threads):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        total_time = time.time() - start
        
        return {
            'method': 'multithreading',
            'num_threads': self.config.num_threads,
            'total_time': total_time,
            'tasks': num_tasks,
            'results': results
        }
    
    def process_sequential(self, num_tasks: int) -> dict:
        """
        Process tasks sequentially (baseline).
        
        Args:
            num_tasks: Number of tasks to process
            
        Returns:
            Benchmark results
        """
        start = time.time()
        
        results = []
        for i in range(num_tasks):
            result = self.cpu_bound_task(i)
            results.append(result)
        
        total_time = time.time() - start
        
        return {
            'method': 'sequential',
            'total_time': total_time,
            'tasks': num_tasks,
            'results': results
        }


def demonstrate_multiprocessing(config: ProcessingConfig, num_tasks: int = 8):
    """Demonstrate multiprocessing capabilities"""
    print("\n" + "="*60)
    print("MULTIPROCESSING DEMONSTRATION")
    print("="*60)
    
    processor = ConfigurableParallelProcessor(config)
    
    print(f"CPU Count: {mp.cpu_count()}")
    print(f"Using {config.num_processes} processes")
    print(f"Workload size: {config.workload_size} KB")
    
    result = processor.process_with_multiprocessing(num_tasks=num_tasks)
    
    print(f"\nTotal execution time: {result['total_time']:.2f} seconds")
    print(f"Tasks processed: {result['tasks']}")
    
    print("\nPer-task details:")
    for r in result['results'][:3]:  # Show first 3
        print(f"  Task {r['task_id']}: {r['execution_time']:.3f}s "
              f"(Process: {r['process_id']})")


def demonstrate_multithreading(config: ProcessingConfig, num_tasks: int = 8):
    """Demonstrate multithreading capabilities"""
    print("\n" + "="*60)
    print("MULTITHREADING DEMONSTRATION")
    print("="*60)
    
    processor = ConfigurableParallelProcessor(config)
    
    print(f"Using {config.num_threads} threads")
    print(f"Workload size: {config.workload_size} KB")
    
    result = processor.process_with_threading(num_tasks=num_tasks)
    
    print(f"\nTotal execution time: {result['total_time']:.2f} seconds")
    print(f"Tasks processed: {result['tasks']}")
    
    print("\nPer-task details:")
    for r in result['results'][:3]:  # Show first 3
        print(f"  Task {r['task_id']}: {r['execution_time']:.3f}s "
              f"(Thread: {r['thread_id']})")


def demonstrate_benchmarking(config: ProcessingConfig, num_tasks: int = 4):
    """Demonstrate benchmarking different approaches"""
    print("\n" + "="*60)
    print("BENCHMARKING: Sequential vs Parallel")
    print("="*60)
    
    processor = ConfigurableParallelProcessor(config)
    
    # Sequential
    print("\nRunning sequential processing...")
    seq_result = processor.process_sequential(num_tasks)
    seq_time = seq_result['total_time']
    print(f"Sequential time: {seq_time:.2f} seconds")
    
    # Multiprocessing
    print("\nRunning multiprocessing...")
    mp_result = processor.process_with_multiprocessing(num_tasks)
    mp_time = mp_result['total_time']
    print(f"Multiprocessing time: {mp_time:.2f} seconds")
    
    # Multithreading
    print("\nRunning multithreading...")
    mt_result = processor.process_with_threading(num_tasks)
    mt_time = mt_result['total_time']
    print(f"Multithreading time: {mt_time:.2f} seconds")
    
    # Calculate speedup
    mp_speedup = seq_time / mp_time if mp_time > 0 else 0
    mt_speedup = seq_time / mt_time if mt_time > 0 else 0
    print(f"Multiprocessing speedup: {mp_speedup:.2f}x")
    print(f"Multithreading speedup: {mt_speedup:.2f}x")


def demonstrate_software_loading(solution_path: str, num_tasks: int = 4, workload_size: int = 100):
    """Demonstrate loading an existing software solution from a Python file."""
    print("\n" + "="*60)
    print("SOFTWARE SOLUTION LOADING")
    print("="*60)
    print(f"Loading solution from: {solution_path}")

    loader = SoftwareSolutionLoader(Path(solution_path))
    results = loader.run(num_tasks=num_tasks, workload_size=workload_size)

    print(f"Loaded solution results ({len(results)} tasks):")
    for r in results[:3]:
        print(f"  {r}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parallel processing and software loader demo"
    )
    parser.add_argument(
        "--mode",
        choices=["multiprocessing", "multithreading", "benchmark", "software"],
        default="benchmark",
        help="Demo mode to run"
    )
    parser.add_argument(
        "--num-processes",
        type=int,
        default=mp.cpu_count(),
        help="Number of processes to use for multiprocessing"
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=4,
        help="Number of threads to use for multithreading"
    )
    parser.add_argument(
        "--workload-size",
        type=int,
        default=100,
        help="Workload size in KB for demo tasks"
    )
    parser.add_argument(
        "--num-tasks",
        type=int,
        default=8,
        help="Number of tasks to execute"
    )
    parser.add_argument(
        "--solution-path",
        type=str,
        default="sample_solution.py",
        help="Path to an external Python solution module"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    config = ProcessingConfig(
        num_processes=args.num_processes,
        num_threads=args.num_threads,
        workload_size=args.workload_size
    )

    if args.mode == "multiprocessing":
        demonstrate_multiprocessing(config, num_tasks=args.num_tasks)
    elif args.mode == "multithreading":
        demonstrate_multithreading(config, num_tasks=args.num_tasks)
    elif args.mode == "benchmark":
        demonstrate_benchmarking(config, num_tasks=args.num_tasks)
    elif args.mode == "software":
        demonstrate_software_loading(
            args.solution_path,
            num_tasks=args.num_tasks,
            workload_size=args.workload_size
        )


if __name__ == "__main__":
    main()
