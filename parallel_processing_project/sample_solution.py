"""Sample software solution to demonstrate runtime loading.

This module acts like an external solution that can be ported into the
parallel processing project via dynamic import.
"""

import time


def run_solution(num_tasks: int = 4, workload_size_kb: int = 100):
    """Run a sample solution that simulates work and returns task results."""
    results = []
    for task_id in range(num_tasks):
        # Simulate task work
        time.sleep(0.05)
        results.append({
            'task_id': task_id,
            'workload_size_kb': workload_size_kb,
            'status': 'completed',
            'checksum': f'sample-{task_id}-{workload_size_kb}'
        })
    return results
