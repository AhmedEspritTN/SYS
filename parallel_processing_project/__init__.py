"""
Parallel Processing & Benchmarking Project
Intensive parallel processing with configurable threads/processes
"""

__title__ = "Parallel Processing & Benchmarking"
__version__ = "1.0"
__author__ = "Course Assignment"
__license__ = "MIT"

# Import main modules for easier access
try:
    from .ipc_communication import (
        PipeCommunication,
        QueueCommunication,
        SharedMemoryData
    )
    from .synchronization import (
        DiningPhilosophers,
        SleepingBarber,
        ProducerConsumerSemaphore
    )
    from .parallel_processing import (
        ConfigurableParallelProcessor,
        ProcessingConfig
    )
except ImportError:
    pass

__all__ = [
    'PipeCommunication',
    'QueueCommunication',
    'SharedMemoryData',
    'DiningPhilosophers',
    'SleepingBarber',
    'ProducerConsumerSemaphore',
    'ConfigurableParallelProcessor',
    'ProcessingConfig'
]
