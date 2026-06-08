"""
Sandbox runner for demo video — executes the real application and captures output.

No presentation slides. Only live app behaviour in an isolated demo file.
"""

import contextlib
import io
import multiprocessing as mp
from pathlib import Path

from file_processing import ParallelFileProcessor, create_sample_file
from parallel_processing import ConfigurableParallelProcessor, ProcessingConfig
from sleeping_barber_processor import SleepingBarberFileProcessor

PROJECT_DIR = Path(__file__).parent
DEMO_FILE = PROJECT_DIR / "demo_sample.bin"


def _user(line: str) -> str:
    return f"> {line}"


def _cmd(line: str) -> str:
    return f"$ {line}"


def capture_lines(func) -> list[str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        func()
    return [line.rstrip() for line in buffer.getvalue().splitlines() if line.strip() or line == ""]


def ensure_demo_file(size_mb: int = 5) -> None:
    create_sample_file(DEMO_FILE, size_mb=size_mb)


def client_menu_lines() -> list[str]:
    return [
        _cmd("python client.py"),
        "",
        "Welcome to the Parallel File Processing Client",
        "Application: large file checksum processing",
        "",
        "=" * 50,
        "  PARALLEL FILE PROCESSING - CLIENT",
        "=" * 50,
        "  1. Process file (Sleeping Barber)",
        "  2. Process file (Multiprocessing)",
        "  3. Process file (Multithreading)",
        "  4. Benchmark all modes",
        "  5. Load external solution",
        "  6. Exit",
        "=" * 50,
    ]


def run_sleeping_barber_demo() -> list[str]:
    def work():
        processor = SleepingBarberFileProcessor(
            file_path=DEMO_FILE,
            chunk_size_kb=512,
            num_barbers=2,
            num_chairs=4,
            show_progress=True,
        )
        result = processor.process_with_sleeping_barber()
        print("\n--- Result ---")
        print(f"Method:     {result.method}")
        print(f"File:       {result.file_path}")
        print(f"Size:       {result.file_size_mb:.2f} MB")
        print(f"Chunks:     {result.chunks_processed}")
        print(f"Workers:    {result.num_workers}")
        print(f"Time:       {result.total_time:.2f} s")
        print(f"Throughput: {result.throughput_mb_per_sec:.2f} MB/s")
        print(f"SHA-256:    {result.file_sha256}")
        print("--------------")

    lines = [
        _user("1"),
        _user("demo_sample.bin"),
        _user("2"),
        _user("4"),
        _user("512"),
        "",
        "--- Sleeping Barber File Service ---",
    ]
    lines.extend(capture_lines(work))
    return lines


def run_multithreading_demo() -> list[str]:
    def work():
        config = ProcessingConfig(
            num_processes=mp.cpu_count(),
            num_threads=2,
            chunk_size_kb=512,
            file_path=str(DEMO_FILE),
        )
        processor = ConfigurableParallelProcessor(config)
        result = processor.process_with_multithreading()
        print("\n--- Result ---")
        print(f"Method:     {result.method}")
        print(f"Chunks:     {result.chunks_processed}")
        print(f"Workers:    {result.num_workers}")
        print(f"Time:       {result.total_time:.2f} s")
        print(f"Throughput: {result.throughput_mb_per_sec:.2f} MB/s")
        print(f"SHA-256:    {result.file_sha256}")

    lines = [
        _user("3"),
        _user("demo_sample.bin"),
        _user("2"),
        _user("512"),
        "",
    ]
    lines.extend(capture_lines(work))
    return lines


def run_benchmark_demo() -> list[str]:
    def work():
        base = ParallelFileProcessor(
            file_path=DEMO_FILE,
            chunk_size_kb=512,
            num_processes=2,
            num_threads=2,
        )
        print("Running sequential...")
        seq = base.process_sequential()
        print(f"  Time: {seq.total_time:.2f}s  |  SHA-256: {seq.file_sha256[:16]}...")

        print("Running multiprocessing...")
        mp_result = base.process_with_multiprocessing()
        print(f"  Time: {mp_result.total_time:.2f}s  |  SHA-256: {mp_result.file_sha256[:16]}...")

        print("Running multithreading...")
        mt_result = base.process_with_multithreading()
        print(f"  Time: {mt_result.total_time:.2f}s  |  SHA-256: {mt_result.file_sha256[:16]}...")

        print("Running Sleeping Barber...")
        barber = SleepingBarberFileProcessor(
            file_path=DEMO_FILE,
            chunk_size_kb=512,
            num_barbers=2,
            num_chairs=4,
            show_progress=False,
        )
        sb = barber.process_with_sleeping_barber()
        print(f"  Time: {sb.total_time:.2f}s  |  SHA-256: {sb.file_sha256[:16]}...")

        match = seq.file_sha256 == mp_result.file_sha256 == mt_result.file_sha256 == sb.file_sha256
        print(f"\nAll checksums match: {match}")
        if seq.total_time > 0:
            print(f"Multithreading speedup: {seq.total_time / mt_result.total_time:.2f}x")
            if sb.total_time > 0:
                print(f"Sleeping Barber speedup: {seq.total_time / sb.total_time:.2f}x")

        base.save_report(PROJECT_DIR / "processing_report.json", {
            "sequential": seq,
            "multiprocessing": mp_result,
            "multithreading": mt_result,
            "sleeping_barber": sb,
        })

    lines = [
        _user("4"),
        _user("demo_sample.bin"),
        _user("2"),
        _user("2"),
        _user("512"),
        "",
    ]
    lines.extend(capture_lines(work))
    return lines


def run_cli_demo() -> list[str]:
    def work():
        import subprocess
        import sys

        cmd = [
            sys.executable,
            "parallel_processing.py",
            str(DEMO_FILE),
            "--mode",
            "sleeping_barber",
            "--num-threads",
            "2",
            "--num-chairs",
            "4",
            "--chunk-size-kb",
            "512",
        ]
        result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)

    lines = [
        _cmd(
            "python parallel_processing.py demo_sample.bin "
            "--mode sleeping_barber --num-threads 2 --num-chairs 4"
        ),
        "",
    ]
    lines.extend(capture_lines(work))
    return lines


def build_all_terminal_sessions() -> dict[str, list[str]]:
    """Run sandbox and return terminal line lists per demo section."""
    ensure_demo_file(size_mb=5)
    return {
        "intro": client_menu_lines(),
        "sleeping_barber": run_sleeping_barber_demo(),
        "multithreading": run_multithreading_demo(),
        "benchmark": run_benchmark_demo(),
        "cli": run_cli_demo(),
    }


if __name__ == "__main__":
    sessions = build_all_terminal_sessions()
    for name, lines in sessions.items():
        print(f"\n{'=' * 60}\nSESSION: {name}\n{'=' * 60}")
        for line in lines[:30]:
            print(line)
        if len(lines) > 30:
            print(f"... ({len(lines) - 30} more lines)")
