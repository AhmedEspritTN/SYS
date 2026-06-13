"""
Sleeping Barber + Dining Philosophers applied to file processing.

Combined mapping:
  Sleeping Barber:
    Customer  -> file chunk that needs hashing
    Barber    -> worker thread (also a philosopher at the table)
    Chairs    -> limited waiting room (bounded queue)
    Shop full -> chunk must wait before entering the queue

  Dining Philosophers:
    Fork      -> shared resource semaphore (one per seat at the table)
    Eat       -> hash a chunk (barber must hold left + right fork first)

Flow:
  1. Chunks arrive and wait in the bounded queue (Sleeping Barber)
  2. A sleeping barber wakes when a customer arrives
  3. Before hashing, the barber acquires both adjacent forks (Dining Philosophers)
  4. Barber processes the chunk, releases forks, and sleeps again
"""

import queue
import threading
import time
from pathlib import Path
from typing import List

from file_processing import (
    ChunkResult,
    FileProcessingResult,
    ParallelFileProcessor,
    process_chunk,
)


class SleepingBarberFileProcessor(ParallelFileProcessor):
    """Process file chunks using Sleeping Barber with Dining Philosophers fork control."""

    def __init__(
        self,
        file_path: Path,
        chunk_size_kb: int = 1024,
        num_barbers: int = 4,
        num_chairs: int = 8,
        show_progress: bool = True,
    ):
        super().__init__(
            file_path=file_path,
            chunk_size_kb=chunk_size_kb,
            num_threads=num_barbers,
        )
        self.num_barbers = num_barbers
        self.num_chairs = num_chairs
        self.show_progress = show_progress

    @staticmethod
    def _acquire_forks(
        barber_id: int,
        num_barbers: int,
        forks: List[threading.Semaphore],
    ) -> None:
        """Acquire both forks in index order to avoid deadlock."""
        left_fork = barber_id
        right_fork = (barber_id + 1) % num_barbers
        first_fork, second_fork = (
            (left_fork, right_fork) if left_fork < right_fork else (right_fork, left_fork)
        )
        forks[first_fork].acquire()
        forks[second_fork].acquire()

    @staticmethod
    def _release_forks(
        barber_id: int,
        num_barbers: int,
        forks: List[threading.Semaphore],
    ) -> None:
        """Release both forks after hashing a chunk."""
        left_fork = barber_id
        right_fork = (barber_id + 1) % num_barbers
        forks[left_fork].release()
        forks[right_fork].release()

    def process_with_sleeping_barber(self) -> FileProcessingResult:
        """
        Process the file using Sleeping Barber queueing and Dining Philosophers forks.

        Steps:
          1. Split file into chunks (customers)
          2. Each chunk waits in the bounded waiting room (chairs)
          3. Barber threads wake up when customers arrive
          4. Barber acquires left + right fork, hashes the chunk, releases forks
          5. Compute the full-file SHA-256 at the end
        """
        start_time = time.time()
        tasks = self._chunk_tasks()
        total_chunks = len(tasks)

        waiting_room: queue.Queue = queue.Queue(maxsize=self.num_chairs)
        customers_waiting = threading.Semaphore(0)
        forks = [threading.Semaphore(1) for _ in range(self.num_barbers)]

        results: List[ChunkResult] = []
        results_lock = threading.Lock()
        stop_event = threading.Event()

        def barber_worker(barber_id: int) -> None:
            """Barber sleeps until a chunk arrives, then eats (hashes) with both forks."""
            while True:
                if not customers_waiting.acquire(timeout=0.2):
                    if stop_event.is_set() and waiting_room.empty():
                        return
                    continue

                try:
                    chunk_task = waiting_room.get(timeout=1)
                except queue.Empty:
                    continue

                if chunk_task is None:
                    waiting_room.task_done()
                    return

                if self.show_progress:
                    print(
                        f"  Barber {barber_id}: customer chunk {chunk_task[3]}, "
                        f"getting forks..."
                    )

                self._acquire_forks(barber_id, self.num_barbers, forks)

                if self.show_progress:
                    print(
                        f"  Barber {barber_id}: eating (hashing chunk {chunk_task[3]})..."
                    )

                result = process_chunk(chunk_task)

                with results_lock:
                    results.append(result)

                self._release_forks(barber_id, self.num_barbers, forks)

                if self.show_progress:
                    print(
                        f"  Barber {barber_id}: done chunk {result.chunk_id} "
                        f"({result.bytes_processed} bytes)"
                    )

                waiting_room.task_done()

        if self.show_progress:
            print("\n--- Sleeping Barber + Dining Philosophers ---")
            print(f"Barbers (philosophers): {self.num_barbers}")
            print(f"Forks:                  {self.num_barbers}")
            print(f"Waiting chairs:         {self.num_chairs}")
            print(f"Chunks to process:      {total_chunks}\n")

        barber_threads = [
            threading.Thread(
                target=barber_worker,
                args=(barber_id,),
                name=f"barber-{barber_id}",
                daemon=True,
            )
            for barber_id in range(self.num_barbers)
        ]

        for thread in barber_threads:
            thread.start()

        for chunk_task in tasks:
            placed = False
            while not placed:
                try:
                    waiting_room.put(chunk_task, block=False)
                    customers_waiting.release()
                    placed = True
                    if self.show_progress:
                        print(
                            f"  Chunk {chunk_task[3]}: entered shop "
                            f"({waiting_room.qsize()}/{self.num_chairs} chairs used)"
                        )
                except queue.Full:
                    if self.show_progress:
                        print(
                            f"  Chunk {chunk_task[3]}: shop full, "
                            f"waiting for a free chair..."
                        )
                    time.sleep(0.02)

        waiting_room.join()
        stop_event.set()

        for _ in range(self.num_barbers):
            customers_waiting.release()
            try:
                waiting_room.put(None, block=False)
            except queue.Full:
                pass

        for thread in barber_threads:
            thread.join(timeout=2)

        file_sha256 = self._compute_file_sha256(self.file_path)
        total_time = time.time() - start_time

        if self.show_progress:
            print(f"\nAll {total_chunks} chunks processed.")
            print(f"File SHA-256: {file_sha256}")

        return self._build_result(
            method="sleeping_barber",
            chunk_results=results,
            total_time=total_time,
            num_workers=self.num_barbers,
            file_sha256=file_sha256,
        )
