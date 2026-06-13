"""
Simple client application for parallel file processing.

This is the user-facing entry point. The user selects a file,
chooses a processing mode, and gets a checksum report.
"""

import multiprocessing as mp
from pathlib import Path

from file_processing import ParallelFileProcessor, create_sample_file
from parallel_processing import (
    ConfigurableParallelProcessor,
    ProcessingConfig,
    SoftwareSolutionLoader,
)
from sleeping_barber_processor import SleepingBarberFileProcessor


def ask_int(prompt: str, default: int, minimum: int = 1) -> int:
    """Read an integer from the user with a default value."""
    try:
        value = input(f"{prompt} [{default}]: ").strip()
    except KeyboardInterrupt:
        raise
    if not value:
        return default
    try:
        number = int(value)
        return max(number, minimum)
    except ValueError:
        print(f"Invalid number, using default: {default}")
        return default


def ask_file_path() -> Path:
    """Ask the user for a file path."""
    path = input("File path [sample_input.bin]: ").strip() or "sample_input.bin"
    file_path = Path(path)

    if not file_path.exists():
        create = input("File not found. Create sample file? (y/n) [y]: ").strip().lower()
        if create in ("", "y", "yes"):
            size_mb = ask_int("Sample size in MB", default=10, minimum=1)
            create_sample_file(file_path, size_mb=size_mb)
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

    return file_path


def print_result(result) -> None:
    """Show processing results to the user."""
    print("\n--- Result ---")
    print(f"Method:     {result.method}")
    print(f"File:       {result.file_path}")
    print(f"Size:       {result.file_size_mb:.2f} MB")
    print(f"Chunks:     {result.chunks_processed}")
    print(f"Workers:    {result.num_workers}")
    print(f"Time:       {result.total_time:.2f} s")
    print(f"Throughput: {result.throughput_mb_per_sec:.2f} MB/s")
    print(f"SHA-256:    {result.file_sha256}")
    print("--------------\n")


def process_sleeping_barber(file_path: Path) -> None:
    """
    Besoin fonctionnel BF-04:
    Process a file with Sleeping Barber queueing and Dining Philosophers forks.
    """
    num_barbers = ask_int("Number of barbers (philosophers)", default=4)
    num_chairs = ask_int("Number of waiting chairs", default=8)

    processor = SleepingBarberFileProcessor(
        file_path=file_path,
        chunk_size_kb=ask_int("Chunk size in KB", default=1024),
        num_barbers=num_barbers,
        num_chairs=num_chairs,
    )
    result = processor.process_with_sleeping_barber()
    print_result(result)


def process_multiprocessing(file_path: Path) -> None:
    """
    Besoin fonctionnel BF-02:
    Process a file using multiple processes (configurable).
    """
    config = ProcessingConfig(
        num_processes=ask_int("Number of processes", default=mp.cpu_count()),
        num_threads=4,
        chunk_size_kb=ask_int("Chunk size in KB", default=1024),
        file_path=str(file_path),
    )
    processor = ConfigurableParallelProcessor(config)
    result = processor.process_with_multiprocessing()
    print_result(result)


def process_multithreading(file_path: Path) -> None:
    """
    Besoin fonctionnel BF-03:
    Process a file using multiple threads (configurable).
    """
    config = ProcessingConfig(
        num_processes=mp.cpu_count(),
        num_threads=ask_int("Number of threads", default=4),
        chunk_size_kb=ask_int("Chunk size in KB", default=1024),
        file_path=str(file_path),
    )
    processor = ConfigurableParallelProcessor(config)
    result = processor.process_with_multithreading()
    print_result(result)


def benchmark_all(file_path: Path) -> None:
    """
    Besoin fonctionnel BF-05:
    Compare sequential, multiprocessing, multithreading, and Sleeping Barber.
    """
    num_processes = ask_int("Number of processes", default=mp.cpu_count())
    num_threads = ask_int("Number of threads / barbers", default=4)
    num_chairs = ask_int("Number of waiting chairs (Sleeping Barber)", default=8)
    chunk_size_kb = ask_int("Chunk size in KB", default=1024)

    base = ParallelFileProcessor(
        file_path=file_path,
        chunk_size_kb=chunk_size_kb,
        num_processes=num_processes,
        num_threads=num_threads,
    )

    print("\nRunning sequential...")
    sequential = base.process_sequential()
    print_result(sequential)

    print("Running multiprocessing...")
    multiprocessing_result = base.process_with_multiprocessing()
    print_result(multiprocessing_result)

    print("Running multithreading...")
    multithreading_result = base.process_with_multithreading()
    print_result(multithreading_result)

    print("Running Sleeping Barber (+ Dining Philosophers)...")
    barber = SleepingBarberFileProcessor(
        file_path=file_path,
        chunk_size_kb=chunk_size_kb,
        num_barbers=num_threads,
        num_chairs=num_chairs,
        show_progress=False,
    )
    barber_result = barber.process_with_sleeping_barber()
    print_result(barber_result)

    checksums_match = (
        sequential.file_sha256
        == multiprocessing_result.file_sha256
        == multithreading_result.file_sha256
        == barber_result.file_sha256
    )
    print(f"All checksums match: {checksums_match}")

    if sequential.total_time > 0:
        print(f"Multiprocessing speedup: {sequential.total_time / multiprocessing_result.total_time:.2f}x")
        print(f"Multithreading speedup:  {sequential.total_time / multithreading_result.total_time:.2f}x")
        print(f"Sleeping Barber speedup: {sequential.total_time / barber_result.total_time:.2f}x")

    try:
        save = input("Save JSON report? (y/n) [y]: ").strip().lower()
    except KeyboardInterrupt:
        print("\nReport not saved.")
        return

    if save in ("", "y", "yes"):
        base.save_report(
            Path("processing_report.json"),
            {
                "sequential": sequential,
                "multiprocessing": multiprocessing_result,
                "multithreading": multithreading_result,
                "sleeping_barber": barber_result,
            },
        )


def load_external_solution(file_path: Path) -> None:
    """
    Besoin fonctionnel BF-06:
    Load and run an external Python processing solution.
    """
    solution_path = input("Solution file [sample_solution.py]: ").strip() or "sample_solution.py"
    num_threads = ask_int("Number of threads", default=4)
    chunk_size_kb = ask_int("Chunk size in KB", default=1024)

    loader = SoftwareSolutionLoader(Path(solution_path))
    result = loader.run(
        file_path=str(file_path),
        chunk_size_kb=chunk_size_kb,
        num_threads=num_threads,
    )

    print("\n--- External Solution Result ---")
    print(f"Method:  {result['method']}")
    print(f"Chunks:  {result['chunks_processed']}")
    print(f"Time:    {result['total_time']:.2f} s")
    print(f"SHA-256: {result['file_sha256']}")
    print("--------------------------------\n")


def show_menu() -> None:
    """Display the main menu."""
    print("\n" + "=" * 50)
    print("  PARALLEL FILE PROCESSING - CLIENT")
    print("=" * 50)
    print("  1. Process file (Sleeping Barber + Dining Philosophers)")
    print("  2. Process file (Multiprocessing)")
    print("  3. Process file (Multithreading)")
    print("  4. Benchmark all modes")
    print("  5. Load external solution")
    print("  6. Exit")
    print("=" * 50)


def main() -> None:
    """Run the interactive client application."""
    print("Welcome to the Parallel File Processing Client")
    print("Application: large file checksum processing")

    try:
        while True:
            show_menu()
            try:
                choice = input("Your choice [1-6]: ").strip()
            except KeyboardInterrupt:
                print("\nGoodbye.")
                break

            if choice == "6":
                print("Goodbye.")
                break

            try:
                file_path = ask_file_path()

                if choice == "1":
                    process_sleeping_barber(file_path)
                elif choice == "2":
                    process_multiprocessing(file_path)
                elif choice == "3":
                    process_multithreading(file_path)
                elif choice == "4":
                    benchmark_all(file_path)
                elif choice == "5":
                    load_external_solution(file_path)
                else:
                    print("Invalid choice. Please enter 1 to 6.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
            except Exception as error:
                print(f"Error: {error}")
    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
