"""
Video Processing Example
Demonstrates parallel processing for real-world video file processing.
Uses multiprocessing to process video frames in parallel.
"""

import time
import os
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
import threading


@dataclass
class ProcessingMetrics:
    """Metrics for processing results"""
    frames_processed: int
    total_time: float
    frames_per_second: float
    processing_time_per_frame: float


class VideoProcessor:
    """
    Simulates video file processing with parallel frame processing.
    In real scenario, this would decode video and process each frame.
    """
    
    def __init__(self, num_workers: int = None):
        """
        Initialize video processor.
        
        Args:
            num_workers: Number of worker processes
        """
        self.num_workers = num_workers or cpu_count()
    
    @staticmethod
    def process_frame(frame_data):
        """
        Process a single video frame.
        In real scenario: edge detection, object tracking, etc.
        
        Args:
            frame_data: Tuple of (frame_id, dummy_frame_size)
            
        Returns:
            Processing result
        """
        frame_id, frame_size = frame_data
        
        # Simulate frame processing
        # In real scenario: apply filters, detect objects, etc.
        time.sleep(0.01)  # Simulate processing time
        
        # Simulate processing result
        return {
            'frame_id': frame_id,
            'detected_objects': frame_id % 5,  # Simulate object detection
            'processing_complete': True
        }
    
    def process_video_sequential(self, num_frames: int) -> ProcessingMetrics:
        """
        Process video frames sequentially (baseline).
        
        Args:
            num_frames: Number of frames to process
            
        Returns:
            Processing metrics
        """
        start_time = time.time()
        
        results = []
        for frame_id in range(num_frames):
            result = self.process_frame((frame_id, 1024))
            results.append(result)
        
        total_time = time.time() - start_time
        fps = num_frames / total_time
        per_frame = total_time / num_frames
        
        return ProcessingMetrics(
            frames_processed=num_frames,
            total_time=total_time,
            frames_per_second=fps,
            processing_time_per_frame=per_frame
        )
    
    def process_video_parallel(self, num_frames: int) -> ProcessingMetrics:
        """
        Process video frames in parallel using multiprocessing.
        
        Args:
            num_frames: Number of frames to process
            
        Returns:
            Processing metrics
        """
        start_time = time.time()
        
        # Create frame data
        frames = [(i, 1024) for i in range(num_frames)]
        
        # Process frames in parallel
        with Pool(processes=self.num_workers) as pool:
            results = pool.map(self.process_frame, frames)
        
        total_time = time.time() - start_time
        fps = num_frames / total_time
        per_frame = total_time / num_frames
        
        return ProcessingMetrics(
            frames_processed=num_frames,
            total_time=total_time,
            frames_per_second=fps,
            processing_time_per_frame=per_frame
        )
    
    def benchmark(self, num_frames: int = 100):
        """
        Benchmark sequential vs parallel processing.
        
        Args:
            num_frames: Number of frames to process
        """
        print("\n" + "="*60)
        print("VIDEO PROCESSING EXAMPLE")
        print("="*60)
        print(f"Processing {num_frames} video frames\n")
        
        # Sequential processing
        print("Sequential processing (1 worker):")
        seq_metrics = self.process_video_sequential(num_frames)
        print(f"  Total time: {seq_metrics.total_time:.2f} seconds")
        print(f"  FPS: {seq_metrics.frames_per_second:.2f} frames/sec")
        print(f"  Per-frame: {seq_metrics.processing_time_per_frame*1000:.2f} ms")
        
        # Parallel processing
        print(f"\nParallel processing ({self.num_workers} workers):")
        par_metrics = self.process_video_parallel(num_frames)
        print(f"  Total time: {par_metrics.total_time:.2f} seconds")
        print(f"  FPS: {par_metrics.frames_per_second:.2f} frames/sec")
        print(f"  Per-frame: {par_metrics.processing_time_per_frame*1000:.2f} ms")
        
        # Speedup
        speedup = seq_metrics.total_time / par_metrics.total_time
        print(f"\nSpeedup: {speedup:.2f}x faster with {self.num_workers} workers")


class LargeFileProcessor:
    """
    Processes large files by splitting into chunks.
    Each chunk is processed by a worker thread/process.
    """
    
    def __init__(self, chunk_size_kb: int = 1024, num_workers: int = 4):
        """
        Initialize file processor.
        
        Args:
            chunk_size_kb: Size of each chunk in KB
            num_workers: Number of worker threads
        """
        self.chunk_size_kb = chunk_size_kb
        self.num_workers = num_workers
    
    @staticmethod
    def process_chunk(chunk_data):
        """
        Process a file chunk.
        
        Args:
            chunk_data: Tuple of (chunk_id, chunk_size_bytes)
            
        Returns:
            Chunk processing result
        """
        chunk_id, chunk_size = chunk_data
        
        # Simulate processing: checksum, compression, analysis, etc.
        time.sleep(0.02)
        
        # Calculate simple checksum (simulation)
        checksum = (chunk_id * 31) % 256
        
        return {
            'chunk_id': chunk_id,
            'bytes_processed': chunk_size,
            'checksum': checksum
        }
    
    def process_file_sequential(self, total_size_mb: int) -> dict:
        """
        Process file sequentially.
        
        Args:
            total_size_mb: Total file size in MB
            
        Returns:
            Processing result
        """
        start_time = time.time()
        
        total_bytes = total_size_mb * 1024 * 1024
        chunk_size_bytes = self.chunk_size_kb * 1024
        num_chunks = total_bytes // chunk_size_bytes
        
        results = []
        for chunk_id in range(num_chunks):
            result = self.process_chunk((chunk_id, chunk_size_bytes))
            results.append(result)
        
        total_time = time.time() - start_time
        
        return {
            'method': 'sequential',
            'total_time': total_time,
            'file_size_mb': total_size_mb,
            'chunks_processed': num_chunks,
            'throughput_mb_per_sec': total_size_mb / total_time
        }
    
    def process_file_parallel(self, total_size_mb: int) -> dict:
        """
        Process file in parallel.
        
        Args:
            total_size_mb: Total file size in MB
            
        Returns:
            Processing result
        """
        start_time = time.time()
        
        total_bytes = total_size_mb * 1024 * 1024
        chunk_size_bytes = self.chunk_size_kb * 1024
        num_chunks = total_bytes // chunk_size_bytes
        
        # Create chunk data
        chunks = [(i, chunk_size_bytes) for i in range(num_chunks)]
        
        # Process chunks in parallel
        with Pool(processes=self.num_workers) as pool:
            results = pool.map(self.process_chunk, chunks)
        
        total_time = time.time() - start_time
        
        return {
            'method': 'parallel',
            'total_time': total_time,
            'file_size_mb': total_size_mb,
            'chunks_processed': num_chunks,
            'throughput_mb_per_sec': total_size_mb / total_time
        }
    
    def benchmark(self, total_size_mb: int = 100):
        """
        Benchmark file processing.
        
        Args:
            total_size_mb: Total file size in MB
        """
        print("\n" + "="*60)
        print("LARGE FILE PROCESSING EXAMPLE")
        print("="*60)
        print(f"Processing {total_size_mb} MB file\n")
        
        # Sequential
        print("Sequential processing:")
        seq_result = self.process_file_sequential(total_size_mb)
        print(f"  Time: {seq_result['total_time']:.2f} seconds")
        print(f"  Throughput: {seq_result['throughput_mb_per_sec']:.2f} MB/s")
        print(f"  Chunks: {seq_result['chunks_processed']}")
        
        # Parallel
        print(f"\nParallel processing ({self.num_workers} workers):")
        par_result = self.process_file_parallel(total_size_mb)
        print(f"  Time: {par_result['total_time']:.2f} seconds")
        print(f"  Throughput: {par_result['throughput_mb_per_sec']:.2f} MB/s")
        print(f"  Chunks: {par_result['chunks_processed']}")
        
        # Speedup
        speedup = seq_result['total_time'] / par_result['total_time']
        print(f"\nSpeedup: {speedup:.2f}x faster")


if __name__ == "__main__":
    # Run video processing example
    video_processor = VideoProcessor(num_workers=cpu_count())
    video_processor.benchmark(num_frames=100)
    
    # Run file processing example
    file_processor = LargeFileProcessor(chunk_size_kb=1024, num_workers=cpu_count())
    file_processor.benchmark(total_size_mb=50)
