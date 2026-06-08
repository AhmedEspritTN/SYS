"""
Real File Processing Example
Demonstrates real file processing with multiprocessing.
Reads a real file in chunks and computes SHA-256 checksums per chunk.
This example benchmarks sequential vs parallel file processing using an actual file.
"""

import argparse
import hashlib
import math
import os
import time
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from pathlib import Path


@dataclass
class FileProcessingMetrics:
    """Metrics for real file processing."""
    file_path: str
    file_size_mb: float
    chunks_processed: int
    total_time: float
    throughput_mb_per_sec: float
    checksum: str


class FileProcessor:
    """Processes a real file by reading it in chunks."""

    def __init__(self, file_path: Path, chunk_size_kb: int = 1024, num_workers: int = None):
        self.file_path = Path(file_path)
        self.chunk_size_kb = chunk_size_kb
        self.chunk_size_bytes = chunk_size_kb * 1024
        self.num_workers = num_workers or cpu_count()

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if not self.file_path.is_file():
            raise ValueError(f"Path must be a regular file: {self.file_path}")

        self.file_size_bytes = self.file_path.stat().st_size
        self.chunks = math.ceil(self.file_size_bytes / self.chunk_size_bytes)

    @staticmethod
    def process_chunk(args):
        """Read a file chunk and compute its SHA-256 checksum."""
        file_path, offset, size = args
        with open(file_path, "rb") as handle:
            handle.seek(offset)
            data = handle.read(size)

        checksum = hashlib.sha256(data).hexdigest()
        return {
            'chunk_id': offset // size,
            'bytes_processed': len(data),
            'chunk_sha256': checksum
        }

    def process_file_sequential(self) -> FileProcessingMetrics:
        """Read the file sequentially and compute a full file checksum."""
        start_time = time.time()
        sha256 = hashlib.sha256()
        chunks_processed = 0

        with open(self.file_path, "rb") as handle:
            while True:
                data = handle.read(self.chunk_size_bytes)
                if not data:
                    break
                sha256.update(data)
                chunks_processed += 1

        total_time = time.time() - start_time
        throughput = (self.file_size_bytes / (1024 * 1024)) / total_time if total_time > 0 else float('inf')

        return FileProcessingMetrics(
            file_path=str(self.file_path),
            file_size_mb=self.file_size_bytes / (1024 * 1024),
            chunks_processed=chunks_processed,
            total_time=total_time,
            throughput_mb_per_sec=throughput,
            checksum=sha256.hexdigest()
        )

    def process_file_parallel(self) -> dict:
        """Read the file in parallel by checking each chunk in a worker process."""
        start_time = time.time()
        offsets = []

        for offset in range(0, self.file_size_bytes, self.chunk_size_bytes):
            size = min(self.chunk_size_bytes, self.file_size_bytes - offset)
            offsets.append((str(self.file_path), offset, size))

        with Pool(processes=self.num_workers) as pool:
            chunk_results = pool.map(self.process_chunk, offsets)

        total_time = time.time() - start_time
        throughput = (self.file_size_bytes / (1024 * 1024)) / total_time if total_time > 0 else float('inf')

        return {
            'method': 'parallel',
            'file_path': str(self.file_path),
            'file_size_mb': self.file_size_bytes / (1024 * 1024),
            'chunks_processed': len(chunk_results),
            'total_time': total_time,
            'throughput_mb_per_sec': throughput,
            'chunk_results': chunk_results
        }

    def benchmark(self):
        """Run sequential and parallel benchmarks for the file."""
        print("\n" + "=" * 60)
        print("REAL FILE PROCESSING EXAMPLE")
        print("=" * 60)
        print(f"Processing file: {self.file_path}")
        print(f"File size: {self.file_size_bytes / (1024 * 1024):.2f} MB")
        print(f"Chunk size: {self.chunk_size_kb} KB")
        print(f"Workers: {self.num_workers}\n")

        seq_metrics = self.process_file_sequential()
        print("Sequential processing:")
        print(f"  Time: {seq_metrics.total_time:.2f} seconds")
        print(f"  Throughput: {seq_metrics.throughput_mb_per_sec:.2f} MB/s")
        print(f"  Chunks: {seq_metrics.chunks_processed}")
        print(f"  SHA-256: {seq_metrics.checksum}\n")

        par_result = self.process_file_parallel()
        print("Parallel processing:")
        print(f"  Time: {par_result['total_time']:.2f} seconds")
        print(f"  Throughput: {par_result['throughput_mb_per_sec']:.2f} MB/s")
        print(f"  Chunks: {par_result['chunks_processed']}")

        example_chunks = par_result['chunk_results'][:3]
        print("  Example chunk checksums:")
        for chunk in example_chunks:
            print(f"    chunk {chunk['chunk_id']}: {chunk['chunk_sha256']}")

        speedup = seq_metrics.total_time / par_result['total_time'] if par_result['total_time'] > 0 else float('inf')
        print(f"\nSpeedup: {speedup:.2f}x faster")


def create_sample_file(file_path: Path, size_mb: int = 10):
    """Create a sample binary file if it does not exist."""
    if file_path.exists():
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)
    total_bytes = size_mb * 1024 * 1024
    chunk = 64 * 1024

    with open(file_path, "wb") as handle:
        written = 0
        while written < total_bytes:
            block_size = min(chunk, total_bytes - written)
            handle.write(os.urandom(block_size))
            written += block_size

    print(f"Created sample file '{file_path}' ({size_mb} MB)")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Real file processing benchmark")
    parser.add_argument(
        "file_path",
        nargs="?",
        default="sample_input.bin",
        help="Path to the file to process"
    )
    parser.add_argument(
        "--chunk-size-kb",
        type=int,
        default=1024,
        help="Chunk size in KB"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes for parallel processing"
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a sample file if the target file does not exist"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    file_path = Path(args.file_path)

    if args.create_sample and not file_path.exists():
        create_sample_file(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"The target file does not exist: {file_path}")

    processor = FileProcessor(
        file_path=file_path,
        chunk_size_kb=args.chunk_size_kb,
        num_workers=args.workers
    )
    processor.benchmark()


if __name__ == "__main__":
    main()
