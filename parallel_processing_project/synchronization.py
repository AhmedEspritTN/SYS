"""
Synchronization Primitives Module
Demonstrates: Semaphores, Locks, and Condition Variables
Classic Problems: Dining Philosophers, Sleeping Barber
"""

import threading
import time
from typing import List
from enum import Enum


class PhilosopherState(Enum):
    """Philosopher states"""
    THINKING = "thinking"
    HUNGRY = "hungry"
    EATING = "eating"


class DiningPhilosophers:
    """
    Classic synchronization problem: Dining Philosophers
    
    Problem: N philosophers sit at a table with N forks.
    Each philosopher needs 2 forks to eat.
    Challenge: Avoid deadlock while maximizing concurrent dining.
    
    Solution: Use semaphores for forks and state array.
    """
    
    def __init__(self, num_philosophers: int = 5):
        """
        Initialize dining philosophers problem.
        
        Args:
            num_philosophers: Number of philosophers
        """
        self.num_philosophers = num_philosophers
        self.forks = [threading.Semaphore(1) for _ in range(num_philosophers)]
        self.state = [PhilosopherState.THINKING] * num_philosophers
        self.state_lock = threading.Lock()
        self.is_eating = [threading.Semaphore(0) for _ in range(num_philosophers)]
    
    def get_forks(self, philosopher_id: int) -> None:
        """
        Philosopher attempts to get both forks.
        Uses Dijkstra's solution with state array.
        
        Args:
            philosopher_id: Philosopher identifier
        """
        left_fork = philosopher_id
        right_fork = (philosopher_id + 1) % self.num_philosophers
        
        # Set state to hungry
        with self.state_lock:
            self.state[philosopher_id] = PhilosopherState.HUNGRY
        
        # Get left fork
        self.forks[left_fork].acquire()
        
        # Get right fork
        self.forks[right_fork].acquire()
        
        # Update state to eating
        with self.state_lock:
            self.state[philosopher_id] = PhilosopherState.EATING
    
    def put_forks(self, philosopher_id: int) -> None:
        """
        Philosopher releases both forks.
        
        Args:
            philosopher_id: Philosopher identifier
        """
        left_fork = philosopher_id
        right_fork = (philosopher_id + 1) % self.num_philosophers
        
        # Update state to thinking
        with self.state_lock:
            self.state[philosopher_id] = PhilosopherState.THINKING
        
        # Release forks
        self.forks[left_fork].release()
        self.forks[right_fork].release()
    
    def philosopher_worker(self, philosopher_id: int, iterations: int):
        """
        Worker function for a philosopher thread.
        
        Args:
            philosopher_id: Philosopher identifier
            iterations: Number of eat/think cycles
        """
        for i in range(iterations):
            # Thinking
            print(f"Philosopher {philosopher_id}: Thinking...")
            time.sleep(0.1)
            
            # Hungry and eating
            print(f"Philosopher {philosopher_id}: Hungry, trying to get forks...")
            self.get_forks(philosopher_id)
            print(f"Philosopher {philosopher_id}: Eating! (cycle {i+1})")
            time.sleep(0.2)
            
            # Release forks
            self.put_forks(philosopher_id)
            print(f"Philosopher {philosopher_id}: Finished eating")


class SleepingBarberState(Enum):
    """Barber and customer states"""
    WAITING = "waiting"
    CUTTING = "cutting"
    SLEEPING = "sleeping"


class SleepingBarber:
    """
    Classic synchronization problem: Sleeping Barber
    
    Problem: A barber cuts hair for customers. If no customers,
    barber sleeps. If shop is full, customers leave.
    
    Challenge: Synchronize barber and customer activities.
    
    Solution: Use semaphores for barber availability,
    customer arrival, and empty chairs.
    """
    
    def __init__(self, num_chairs: int = 3):
        """
        Initialize sleeping barber problem.
        
        Args:
            num_chairs: Number of waiting chairs
        """
        self.num_chairs = num_chairs
        self.waiting_customers = 0
        self.customer_count = 0
        
        # Semaphores
        self.customers_waiting = threading.Semaphore(0)  # Customers in queue
        self.barber_available = threading.Semaphore(0)   # Barber free
        self.access_lock = threading.Lock()              # Protect shared data
    
    def customer_worker(self, customer_id: int):
        """
        Customer attempts to get haircut.
        
        Args:
            customer_id: Customer identifier
        """
        with self.access_lock:
            if self.waiting_customers < self.num_chairs:
                # Sit in waiting room
                self.waiting_customers += 1
                print(f"Customer {customer_id}: Waiting for barber "
                      f"({self.waiting_customers} customers waiting)")
                
                # Signal barber
                self.customers_waiting.release()
            else:
                # Shop is full, customer leaves
                print(f"Customer {customer_id}: Shop full, leaving!")
                return
        
        # Wait for barber
        self.barber_available.acquire()
        
        with self.access_lock:
            self.waiting_customers -= 1
        
        print(f"Customer {customer_id}: Getting haircut...")
        time.sleep(0.3)
        print(f"Customer {customer_id}: Finished, leaving satisfied")
    
    def barber_worker(self, num_customers_to_serve: int):
        """
        Barber cuts hair for customers.
        
        Args:
            num_customers_to_serve: Number of customers to serve
        """
        for i in range(num_customers_to_serve):
            # Wait for customer
            self.customers_waiting.acquire()
            
            print(f"Barber: Starting haircut for customer {i+1}...")
            time.sleep(0.3)
            print(f"Barber: Finished haircut {i+1}")
            
            # Signal customer
            self.barber_available.release()
        
        print("Barber: All customers served, closing shop")


class ProducerConsumerSemaphore:
    """
    Producer-Consumer problem using semaphores.
    
    Multiple producers produce items into a bounded buffer.
    Multiple consumers consume items from the buffer.
    Must maintain: capacity constraint and synchronization.
    """
    
    def __init__(self, buffer_size: int = 5):
        """
        Initialize producer-consumer with semaphores.
        
        Args:
            buffer_size: Maximum buffer capacity
        """
        self.buffer = []
        self.buffer_size = buffer_size
        self.buffer_lock = threading.Lock()
        
        # Semaphores
        self.empty = threading.Semaphore(buffer_size)  # Empty slots
        self.full = threading.Semaphore(0)              # Full slots
    
    def produce(self, item: str) -> None:
        """
        Producer adds item to buffer.
        
        Args:
            item: Item to produce
        """
        # Wait for empty slot
        self.empty.acquire()
        
        with self.buffer_lock:
            self.buffer.append(item)
            print(f"Produced: {item}, Buffer: {self.buffer}")
        
        # Signal full slot
        self.full.release()
    
    def consume(self) -> str:
        """
        Consumer removes item from buffer.
        
        Returns:
            Consumed item
        """
        # Wait for full slot
        self.full.acquire()
        
        with self.buffer_lock:
            item = self.buffer.pop(0)
            print(f"Consumed: {item}, Buffer: {self.buffer}")
        
        # Signal empty slot
        self.empty.release()
        
        return item


def demonstrate_dining_philosophers():
    """Demonstrate dining philosophers problem"""
    print("\n" + "="*60)
    print("DINING PHILOSOPHERS PROBLEM")
    print("="*60)
    
    num_philosophers = 5
    philosophers = DiningPhilosophers(num_philosophers)
    
    # Create philosopher threads
    threads = []
    for i in range(num_philosophers):
        t = threading.Thread(
            target=philosophers.philosopher_worker,
            args=(i, 2)  # 2 cycles per philosopher
        )
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("All philosophers finished!")


def demonstrate_sleeping_barber():
    """Demonstrate sleeping barber problem"""
    print("\n" + "="*60)
    print("SLEEPING BARBER PROBLEM")
    print("="*60)
    
    barber_shop = SleepingBarber(num_chairs=3)
    
    # Create barber thread
    barber = threading.Thread(
        target=barber_shop.barber_worker,
        args=(8,)  # Serve 8 customers
    )
    barber.start()
    
    # Create customer threads
    customers = []
    for i in range(10):
        t = threading.Thread(
            target=barber_shop.customer_worker,
            args=(i,)
        )
        customers.append(t)
        t.start()
        time.sleep(0.05)  # Stagger customer arrivals
    
    barber.join()
    for c in customers:
        c.join()
    
    print("Barber shop closed!")


def demonstrate_producer_consumer():
    """Demonstrate producer-consumer problem"""
    print("\n" + "="*60)
    print("PRODUCER-CONSUMER PROBLEM (with Semaphores)")
    print("="*60)
    
    pc = ProducerConsumerSemaphore(buffer_size=3)
    
    # Create producer threads
    producers = []
    for i in range(2):
        t = threading.Thread(
            target=lambda pid=i: [
                pc.produce(f"Item_P{pid}_{j}") 
                for j in range(3)
            ]
        )
        producers.append(t)
        t.start()
    
    # Create consumer threads
    consumers = []
    for i in range(2):
        t = threading.Thread(
            target=lambda cid=i: [
                pc.consume() 
                for _ in range(3)
            ]
        )
        consumers.append(t)
        t.start()
    
    for t in producers + consumers:
        t.join()
    
    print("Producer-Consumer finished!")


if __name__ == "__main__":
    demonstrate_dining_philosophers()
    demonstrate_sleeping_barber()
    demonstrate_producer_consumer()
