"""
Multiprocessing and multithreading utilities for parallel file processing.
"""

import argparse
import importlib.util
import multiprocessing as mp
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Any, Optional

from file_processing import ParallelFileProcessor, create_sample_file, FileProcessingResult
from sleeping_barber_processor import SleepingBarberFileProcessor


@dataclass
class ProcessingConfig:
    """Configuration for parallel file processing."""
    num_processes: int
    num_threads: int
    chunk_size_kb: int = 1024
    file_path: Optional[str] = None


class MultiprocessingPool:
    """Pool of worker processes for parallel processing."""

    def __init__(self, num_processes: int = None):
        if num_processes is None:
            num_processes = mp.cpu_count()

        self.num_processes = num_processes
        self.pool = mp.Pool(processes=num_processes)

    def map_work(self, func: Callable, items: List[Any]) -> List[Any]:
        return self.pool.map(func, items)

    def close(self):
        self.pool.close()
        self.pool.join()


class ThreadPool:
    """Pool of worker threads for parallel processing."""

    def __init__(self, num_threads: int = 4):
        self.num_threads = num_threads
        self.threads = []
        self.task_queue = queue.Queue()
        self.results = []
        self.results_lock = threading.Lock()

    def worker_thread(self, thread_id: int):
        processed_count = 0

        while True:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
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
        self.task_queue.put((func, args, kwargs))

    def start_workers(self):
        self.task_queue = queue.Queue()
        self.results = []
        self.threads = []

        for index in range(self.num_threads):
            thread = threading.Thread(target=self.worker_thread, args=(index,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

    def wait_completion(self):
        for _ in range(self.num_threads):
            self.task_queue.put(None)
        for thread in self.threads:
            thread.join()
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
            str(self.solution_path),
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {self.solution_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run(self, file_path: str, chunk_size_kb: int = 1024, num_threads: int = 4):
        module = self.load()
        if hasattr(module, "run_solution"):
            return module.run_solution(
                file_path=file_path,
                chunk_size_kb=chunk_size_kb,
                num_threads=num_threads,
            )
        raise AttributeError(
            "Loaded module must define run_solution(file_path, chunk_size_kb, num_threads)"
        )


class ConfigurableParallelProcessor:
    """Configurable file processor using sequential, multiprocessing, or multithreading."""

    def __init__(self, config: ProcessingConfig):
        self.config = config
        if not config.file_path:
            raise ValueError("ProcessingConfig.file_path is required for file processing")

        self.processor = ParallelFileProcessor(
            file_path=Path(config.file_path),
            chunk_size_kb=config.chunk_size_kb,
            num_processes=config.num_processes,
            num_threads=config.num_threads,
        )

    def process_sequential(self) -> FileProcessingResult:
        return self.processor.process_sequential()

    def process_with_multiprocessing(self) -> FileProcessingResult:
        return self.processor.process_with_multiprocessing()

    def process_with_multithreading(self) -> FileProcessingResult:
        return self.processor.process_with_multithreading()

    def benchmark(self) -> dict:
        return self.processor.benchmark()

    def save_report(self, output_path: Path, results: dict) -> Path:
        return self.processor.save_report(output_path, results)


def _default_config(file_path: str, num_processes: int = None, num_threads: int = 4) -> ProcessingConfig:
    return ProcessingConfig(
        num_processes=num_processes or mp.cpu_count(),
        num_threads=num_threads,
        chunk_size_kb=1024,
        file_path=file_path,
    )


def _print_result_summary(result: FileProcessingResult) -> None:
    print(f"Method: {result.method}")
    print(f"Time: {result.total_time:.2f} seconds")
    print(f"Throughput: {result.throughput_mb_per_sec:.2f} MB/s")
    print(f"Chunks: {result.chunks_processed}")
    print(f"Workers: {result.num_workers}")
    print(f"File SHA-256: {result.file_sha256}")


def demonstrate_multiprocessing(
    config: ProcessingConfig,
    output_report: Optional[str] = None,
):
    """Run file processing with multiprocessing."""
    print("\n" + "=" * 60)
    print("MULTIPROCESSING FILE PROCESSING")
    print("=" * 60)

    processor = ConfigurableParallelProcessor(config)
    print(f"CPU count: {mp.cpu_count()}")
    print(f"File: {config.file_path}")
    print(f"Processes: {config.num_processes}")
    print(f"Chunk size: {config.chunk_size_kb} KB\n")

    result = processor.process_with_multiprocessing()
    _print_result_summary(result)

    if output_report:
        processor.save_report(Path(output_report), {"multiprocessing": result})


def demonstrate_multithreading(
    config: ProcessingConfig,
    output_report: Optional[str] = None,
):
    """Run file processing with multithreading."""
    print("\n" + "=" * 60)
    print("MULTITHREADING FILE PROCESSING")
    print("=" * 60)

    processor = ConfigurableParallelProcessor(config)
    print(f"File: {config.file_path}")
    print(f"Threads: {config.num_threads}")
    print(f"Chunk size: {config.chunk_size_kb} KB\n")

    result = processor.process_with_multithreading()
    _print_result_summary(result)

    if output_report:
        processor.save_report(Path(output_report), {"multithreading": result})


def demonstrate_sleeping_barber(
    config: ProcessingConfig,
    num_chairs: int = 8,
    output_report: Optional[str] = None,
):
    """Run file processing with the Sleeping Barber algorithm."""
    print("\n" + "=" * 60)
    print("SLEEPING BARBER FILE PROCESSING")
    print("=" * 60)

    processor = SleepingBarberFileProcessor(
        file_path=Path(config.file_path),
        chunk_size_kb=config.chunk_size_kb,
        num_barbers=config.num_threads,
        num_chairs=num_chairs,
    )
    print(f"File: {config.file_path}")
    print(f"Barbers (threads): {config.num_threads}")
    print(f"Waiting chairs: {num_chairs}")
    print(f"Chunk size: {config.chunk_size_kb} KB\n")

    result = processor.process_with_sleeping_barber()
    _print_result_summary(result)

    if output_report:
        processor.save_report(Path(output_report), {"sleeping_barber": result})


def demonstrate_benchmarking(
    config: ProcessingConfig,
    output_report: Optional[str] = None,
    num_chairs: int = 8,
):
    """Benchmark all file processing modes including Sleeping Barber."""
    processor = ConfigurableParallelProcessor(config)
    results = processor.benchmark()

    barber = SleepingBarberFileProcessor(
        file_path=Path(config.file_path),
        chunk_size_kb=config.chunk_size_kb,
        num_barbers=config.num_threads,
        num_chairs=num_chairs,
        show_progress=False,
    )
    barber_result = barber.process_with_sleeping_barber()
    results["sleeping_barber"] = barber_result
    _print_result_summary(barber_result)

    if output_report:
        processor.save_report(Path(output_report), results)


def demonstrate_software_loading(
    solution_path: str,
    file_path: str,
    chunk_size_kb: int = 1024,
    num_threads: int = 4,
):
    """Load and run an external file-processing solution module."""
    print("\n" + "=" * 60)
    print("SOFTWARE SOLUTION LOADING")
    print("=" * 60)
    print(f"Loading solution from: {solution_path}")
    print(f"Processing file: {file_path}")

    loader = SoftwareSolutionLoader(Path(solution_path))
    result = loader.run(
        file_path=file_path,
        chunk_size_kb=chunk_size_kb,
        num_threads=num_threads,
    )

    print(f"Loaded solution processed {result['chunks_processed']} chunks")
    print(f"File SHA-256: {result['file_sha256']}")
    print(f"Time: {result['total_time']:.2f} seconds")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parallel file processing with multiprocessing and multithreading"
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        default="sample_input.bin",
        help="Path to the file to process",
    )
    parser.add_argument(
        "--mode",
        choices=[
            "sequential",
            "multiprocessing",
            "multithreading",
            "sleeping_barber",
            "benchmark",
            "software",
        ],
        default="benchmark",
        help="Processing mode to run",
    )
    parser.add_argument(
        "--num-processes",
        type=int,
        default=mp.cpu_count(),
        help="Number of processes for multiprocessing",
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=4,
        help="Number of threads for multithreading",
    )
    parser.add_argument(
        "--chunk-size-kb",
        type=int,
        default=1024,
        help="Chunk size in KB",
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a sample file if the target file does not exist",
    )
    parser.add_argument(
        "--sample-size-mb",
        type=int,
        default=10,
        help="Sample file size in MB when using --create-sample",
    )
    parser.add_argument(
        "--output-report",
        type=str,
        default=None,
        help="Optional JSON report output path",
    )
    parser.add_argument(
        "--num-chairs",
        type=int,
        default=8,
        help="Waiting chairs for Sleeping Barber mode",
    )
    parser.add_argument(
        "--solution-path",
        type=str,
        default="sample_solution.py",
        help="Path to an external Python solution module",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    file_path = Path(args.file_path)

    if args.create_sample and not file_path.exists():
        create_sample_file(file_path, size_mb=args.sample_size_mb)

    if not file_path.exists():
        raise FileNotFoundError(f"The target file does not exist: {file_path}")

    config = ProcessingConfig(
        num_processes=args.num_processes,
        num_threads=args.num_threads,
        chunk_size_kb=args.chunk_size_kb,
        file_path=str(file_path),
    )
    processor = ConfigurableParallelProcessor(config)

    if args.mode == "sequential":
        result = processor.process_sequential()
        _print_result_summary(result)
        if args.output_report:
            processor.save_report(Path(args.output_report), {"sequential": result})
    elif args.mode == "multiprocessing":
        demonstrate_multiprocessing(config, output_report=args.output_report)
    elif args.mode == "multithreading":
        demonstrate_multithreading(config, output_report=args.output_report)
    elif args.mode == "sleeping_barber":
        demonstrate_sleeping_barber(
            config,
            num_chairs=args.num_chairs,
            output_report=args.output_report,
        )
    elif args.mode == "benchmark":
        demonstrate_benchmarking(
            config,
            output_report=args.output_report,
            num_chairs=args.num_chairs,
        )
    elif args.mode == "software":
        demonstrate_software_loading(
            args.solution_path,
            file_path=str(file_path),
            chunk_size_kb=args.chunk_size_kb,
            num_threads=args.num_threads,
        )


if __name__ == "__main__":
    main()
