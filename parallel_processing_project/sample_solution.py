"""External file-processing solution loaded at runtime."""

import hashlib
import threading
import time
from pathlib import Path

from file_processing import process_chunk


def run_solution(file_path: str, chunk_size_kb: int = 1024, num_threads: int = 4):
    """
    Process a file using multithreading.

    This module is loaded dynamically by SoftwareSolutionLoader.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    file_size = path.stat().st_size
    chunk_size_bytes = chunk_size_kb * 1024
    tasks = []

    chunk_id = 0
    for offset in range(0, file_size, chunk_size_bytes):
        size = min(chunk_size_bytes, file_size - offset)
        tasks.append((str(path), offset, size, chunk_id))
        chunk_id += 1

    start_time = time.time()
    results = []
    lock = threading.Lock()
    task_index = {"value": 0}
    index_lock = threading.Lock()

    def worker():
        while True:
            with index_lock:
                if task_index["value"] >= len(tasks):
                    return
                task = tasks[task_index["value"]]
                task_index["value"] += 1

            chunk_result = process_chunk(task)
            with lock:
                results.append(chunk_result)

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    sha256 = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            data = handle.read(chunk_size_bytes)
            if not data:
                break
            sha256.update(data)

    total_time = time.time() - start_time

    return {
        "file_path": str(path),
        "chunks_processed": len(results),
        "total_time": total_time,
        "file_sha256": sha256.hexdigest(),
        "method": "external_multithreading",
        "num_threads": num_threads,
    }
