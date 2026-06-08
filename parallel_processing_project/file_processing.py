"""
Parallel file processing engine.

Reads a file in chunks and computes SHA-256 checksums using sequential,
multiprocessing, or multithreading execution.
"""

import hashlib
import json
import math
import multiprocessing as mp
import os
import queue
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ChunkResult:
    """Result from processing a single file chunk."""
    chunk_id: int
    offset: int
    bytes_processed: int
    chunk_sha256: str
    execution_time: float


@dataclass
class FileProcessingResult:
    """Aggregated result from a file processing run."""
    method: str
    file_path: str
    file_size_mb: float
    chunks_processed: int
    total_time: float
    throughput_mb_per_sec: float
    file_sha256: str
    num_workers: int
    chunk_results: List[ChunkResult] = field(default_factory=list)


def process_chunk(task: tuple) -> ChunkResult:
    """
    Read a file chunk and compute its SHA-256 checksum.

    Args:
        task: (file_path, offset, size, chunk_id)
    """
    file_path, offset, size, chunk_id = task
    start = time.time()

    with open(file_path, "rb") as handle:
        handle.seek(offset)
        data = handle.read(size)

    checksum = hashlib.sha256(data).hexdigest()
    elapsed = time.time() - start

    return ChunkResult(
        chunk_id=chunk_id,
        offset=offset,
        bytes_processed=len(data),
        chunk_sha256=checksum,
        execution_time=elapsed,
    )


def create_sample_file(file_path: Path, size_mb: int = 10) -> None:
    """Create a sample binary file if it does not exist."""
    if file_path.exists():
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)
    total_bytes = size_mb * 1024 * 1024
    block_size = 64 * 1024

    with open(file_path, "wb") as handle:
        written = 0
        while written < total_bytes:
            current_block = min(block_size, total_bytes - written)
            handle.write(os.urandom(current_block))
            written += current_block

    print(f"Created sample file '{file_path}' ({size_mb} MB)")


class ParallelFileProcessor:
    """Process files using sequential, multiprocessing, or multithreading."""

    def __init__(
        self,
        file_path: Path,
        chunk_size_kb: int = 1024,
        num_processes: Optional[int] = None,
        num_threads: int = 4,
    ):
        self.file_path = Path(file_path)
        self.chunk_size_kb = chunk_size_kb
        self.chunk_size_bytes = chunk_size_kb * 1024
        self.num_processes = num_processes or mp.cpu_count()
        self.num_threads = num_threads

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if not self.file_path.is_file():
            raise ValueError(f"Path must be a regular file: {self.file_path}")

        self.file_size_bytes = self.file_path.stat().st_size

    def _chunk_tasks(self) -> List[tuple]:
        """Build chunk tasks as (file_path, offset, size, chunk_id)."""
        tasks = []
        chunk_id = 0

        for offset in range(0, self.file_size_bytes, self.chunk_size_bytes):
            size = min(self.chunk_size_bytes, self.file_size_bytes - offset)
            tasks.append((str(self.file_path), offset, size, chunk_id))
            chunk_id += 1

        return tasks

    @staticmethod
    def _compute_file_sha256(file_path: Path) -> str:
        """Compute the full-file SHA-256 checksum."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as handle:
            while True:
                data = handle.read(1024 * 1024)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()

    def _build_result(
        self,
        method: str,
        chunk_results: List[ChunkResult],
        total_time: float,
        num_workers: int,
        file_sha256: str,
    ) -> FileProcessingResult:
        throughput = (
            (self.file_size_bytes / (1024 * 1024)) / total_time
            if total_time > 0
            else float("inf")
        )

        return FileProcessingResult(
            method=method,
            file_path=str(self.file_path),
            file_size_mb=self.file_size_bytes / (1024 * 1024),
            chunks_processed=len(chunk_results),
            total_time=total_time,
            throughput_mb_per_sec=throughput,
            file_sha256=file_sha256,
            num_workers=num_workers,
            chunk_results=sorted(chunk_results, key=lambda item: item.chunk_id),
        )

    def process_sequential(self) -> FileProcessingResult:
        """Read and hash the file sequentially."""
        start_time = time.time()
        chunk_results = []

        with open(self.file_path, "rb") as handle:
            chunk_id = 0
            while True:
                chunk_start = time.time()
                data = handle.read(self.chunk_size_bytes)
                if not data:
                    break

                chunk_results.append(
                    ChunkResult(
                        chunk_id=chunk_id,
                        offset=handle.tell() - len(data),
                        bytes_processed=len(data),
                        chunk_sha256=hashlib.sha256(data).hexdigest(),
                        execution_time=time.time() - chunk_start,
                    )
                )
                chunk_id += 1

        file_sha256 = self._compute_file_sha256(self.file_path)
        total_time = time.time() - start_time

        return self._build_result(
            method="sequential",
            chunk_results=chunk_results,
            total_time=total_time,
            num_workers=1,
            file_sha256=file_sha256,
        )

    def process_with_multiprocessing(self) -> FileProcessingResult:
        """Process file chunks in parallel using multiple processes."""
        start_time = time.time()
        tasks = self._chunk_tasks()

        with mp.Pool(processes=self.num_processes) as pool:
            chunk_results = pool.map(process_chunk, tasks)

        file_sha256 = self._compute_file_sha256(self.file_path)
        total_time = time.time() - start_time

        return self._build_result(
            method="multiprocessing",
            chunk_results=chunk_results,
            total_time=total_time,
            num_workers=self.num_processes,
            file_sha256=file_sha256,
        )

    def process_with_multithreading(self) -> FileProcessingResult:
        """Process file chunks in parallel using multiple threads."""
        start_time = time.time()
        tasks = self._chunk_tasks()
        chunk_results: List[ChunkResult] = []
        results_lock = threading.Lock()
        task_queue: queue.Queue = queue.Queue()

        for task in tasks:
            task_queue.put(task)

        def worker() -> None:
            while True:
                try:
                    task = task_queue.get_nowait()
                except queue.Empty:
                    break

                result = process_chunk(task)
                with results_lock:
                    chunk_results.append(result)
                task_queue.task_done()

        threads = [
            threading.Thread(target=worker, name=f"file-worker-{index}")
            for index in range(self.num_threads)
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        file_sha256 = self._compute_file_sha256(self.file_path)
        total_time = time.time() - start_time

        return self._build_result(
            method="multithreading",
            chunk_results=chunk_results,
            total_time=total_time,
            num_workers=self.num_threads,
            file_sha256=file_sha256,
        )

    def benchmark(self) -> dict:
        """Run sequential, multiprocessing, and multithreading benchmarks."""
        print("\n" + "=" * 60)
        print("FILE PROCESSING BENCHMARK")
        print("=" * 60)
        print(f"File: {self.file_path}")
        print(f"Size: {self.file_size_bytes / (1024 * 1024):.2f} MB")
        print(f"Chunk size: {self.chunk_size_kb} KB")
        print(f"Chunks: {math.ceil(self.file_size_bytes / self.chunk_size_bytes)}")
        print(f"Processes: {self.num_processes}")
        print(f"Threads: {self.num_threads}\n")

        sequential = self.process_sequential()
        multiprocessing_result = self.process_with_multiprocessing()
        multithreading_result = self.process_with_multithreading()

        results = {
            "sequential": sequential,
            "multiprocessing": multiprocessing_result,
            "multithreading": multithreading_result,
        }

        for name, result in results.items():
            print(f"{name.capitalize()}:")
            print(f"  Time: {result.total_time:.2f} s")
            print(f"  Throughput: {result.throughput_mb_per_sec:.2f} MB/s")
            print(f"  Chunks: {result.chunks_processed}")
            print(f"  Workers: {result.num_workers}")
            print(f"  File SHA-256: {result.file_sha256}")

            if result.chunk_results:
                sample = result.chunk_results[:2]
                print("  Sample chunk hashes:")
                for chunk in sample:
                    print(f"    chunk {chunk.chunk_id}: {chunk.chunk_sha256}")
            print()

        checksums_match = (
            sequential.file_sha256
            == multiprocessing_result.file_sha256
            == multithreading_result.file_sha256
        )
        print(f"Checksums match across all methods: {checksums_match}")

        if sequential.total_time > 0:
            mp_speedup = sequential.total_time / multiprocessing_result.total_time
            mt_speedup = sequential.total_time / multithreading_result.total_time
            print(f"Multiprocessing speedup: {mp_speedup:.2f}x")
            print(f"Multithreading speedup: {mt_speedup:.2f}x")

        return results

    def save_report(self, output_path: Path, results: dict) -> Path:
        """Save benchmark results to a JSON report file."""
        output_path = Path(output_path)
        payload = {
            "file_path": str(self.file_path),
            "file_size_bytes": self.file_size_bytes,
            "chunk_size_kb": self.chunk_size_kb,
            "methods": {},
        }

        for name, result in results.items():
            payload["methods"][name] = {
                "total_time": result.total_time,
                "throughput_mb_per_sec": result.throughput_mb_per_sec,
                "chunks_processed": result.chunks_processed,
                "num_workers": result.num_workers,
                "file_sha256": result.file_sha256,
                "chunks": [
                    {
                        "chunk_id": chunk.chunk_id,
                        "offset": chunk.offset,
                        "bytes_processed": chunk.bytes_processed,
                        "chunk_sha256": chunk.chunk_sha256,
                        "execution_time": chunk.execution_time,
                    }
                    for chunk in result.chunk_results
                ],
            }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        print(f"Report saved to: {output_path}")
        return output_path
