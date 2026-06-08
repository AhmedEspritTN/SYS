"""
Parallel Processing & Benchmarking Project
Parallel file processing with configurable threads/processes
"""

__title__ = "Parallel Processing & Benchmarking"
__version__ = "1.2"
__author__ = "Course Assignment"
__license__ = "MIT"

try:
    from .ipc_communication import (
        PipeCommunication,
        QueueCommunication,
        SharedMemoryData,
    )
    from .synchronization import (
        DiningPhilosophers,
        SleepingBarber,
        ProducerConsumerSemaphore,
    )
    from .parallel_processing import (
        ConfigurableParallelProcessor,
        ProcessingConfig,
    )
    from .file_processing import (
        ParallelFileProcessor,
        FileProcessingResult,
        create_sample_file,
    )
    from .sleeping_barber_processor import SleepingBarberFileProcessor
except ImportError:
    pass

__all__ = [
    "PipeCommunication",
    "QueueCommunication",
    "SharedMemoryData",
    "DiningPhilosophers",
    "SleepingBarber",
    "ProducerConsumerSemaphore",
    "ConfigurableParallelProcessor",
    "ProcessingConfig",
    "ParallelFileProcessor",
    "FileProcessingResult",
    "SleepingBarberFileProcessor",
    "create_sample_file",
]
