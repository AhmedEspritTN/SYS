"""
Real file processing entry point.

Uses the shared file_processing engine for sequential, multiprocessing,
and multithreading execution.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from file_processing import ParallelFileProcessor, create_sample_file


def parse_arguments():
    parser = argparse.ArgumentParser(description="Parallel file processing")
    parser.add_argument(
        "file_path",
        nargs="?",
        default="sample_input.bin",
        help="Path to the file to process",
    )
    parser.add_argument(
        "--mode",
        choices=["sequential", "multiprocessing", "multithreading", "benchmark"],
        default="benchmark",
        help="Processing mode",
    )
    parser.add_argument(
        "--chunk-size-kb",
        type=int,
        default=1024,
        help="Chunk size in KB",
    )
    parser.add_argument(
        "--num-processes",
        type=int,
        default=None,
        help="Number of worker processes",
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=4,
        help="Number of worker threads",
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
        help="Sample file size in MB",
    )
    parser.add_argument(
        "--output-report",
        type=str,
        default=None,
        help="Optional JSON report output path",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    file_path = Path(args.file_path)

    if args.create_sample and not file_path.exists():
        create_sample_file(file_path, size_mb=args.sample_size_mb)

    if not file_path.exists():
        raise FileNotFoundError(f"The target file does not exist: {file_path}")

    processor = ParallelFileProcessor(
        file_path=file_path,
        chunk_size_kb=args.chunk_size_kb,
        num_processes=args.num_processes,
        num_threads=args.num_threads,
    )

    if args.mode == "sequential":
        result = processor.process_sequential()
        print(f"Processed {result.chunks_processed} chunks in {result.total_time:.2f}s")
        print(f"File SHA-256: {result.file_sha256}")
    elif args.mode == "multiprocessing":
        result = processor.process_with_multiprocessing()
        print(f"Processed {result.chunks_processed} chunks in {result.total_time:.2f}s")
        print(f"File SHA-256: {result.file_sha256}")
    elif args.mode == "multithreading":
        result = processor.process_with_multithreading()
        print(f"Processed {result.chunks_processed} chunks in {result.total_time:.2f}s")
        print(f"File SHA-256: {result.file_sha256}")
    else:
        results = processor.benchmark()
        if args.output_report:
            processor.save_report(Path(args.output_report), results)


if __name__ == "__main__":
    main()
