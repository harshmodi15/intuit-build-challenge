"""
Assignment 1: Producer–Consumer Pattern using Thread Synchronization

This module demonstrates a classic producer–consumer workflow based on
Python concurrency primitives. It includes:

    - Producers that read from a thread-safe source container.
    - Consumers that drain a bounded blocking queue.
    - A FIFO queue with blocking semantics using Condition variables.
    - Optional production/consumption delay simulation.
    - A system orchestrator that wires everything together.

The implementation emphasizes correctness, clarity, and teaching value:
    - Full FIFO ordering
    - Race-free container access
    - Proper wait/notify signaling
    - No busy-waiting
"""

import threading
import time
from typing import Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Part 1: Item
@dataclass
class Item:
    """
    Represents a data unit flowing between producer and consumer.

    Attributes:
        id: Unique identifier for the item.
        data: Arbitrary payload.
        timestamp: Auto-populated creation time unless supplied.
    """

    id: int
    data: Any
    timestamp: float = None

    def __post_init__(self):
        # Auto-create timestamp if none was provided.
        if self.timestamp is None:
            self.timestamp = time.time()

    def __repr__(self):
        return f"Item(id={self.id}, data={self.data})"


# Part 2: BoundedBlockingQueue
class BoundedBlockingQueue:
    """
    A FIFO queue with a strict maximum capacity and blocking semantics.

    Behavioral guarantees:
        - put() blocks if the queue is full.
        - get() blocks if the queue is empty.
        - FIFO ordering is maintained via deque.
        - All operations are race-free using a shared lock.

    Internals:
        lock       → provides atomic access.
        not_full   → producers wait here when queue is full.
        not_empty  → consumers wait here when queue is empty.
    """

    def __init__(self, capacity: int = 10):
        if capacity <= 0:
            raise ValueError("Queue capacity must be positive")

        self.capacity = capacity
        self.queue = deque()
        self.lock = threading.Lock()

        # Both conditions share the same lock.
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    # PUT OPERATION (BLOCKING)
    def put(self, item: Any, timeout: Optional[float] = None) -> bool:
        """
        Insert an item into the queue. If the queue is full, blocks until a
        consumer removes an element or timeout occurs.

        Args:
            item: The object to enqueue.
            timeout: Optional max wait time.

        Returns:
            True if the enqueue succeeds.
            False if timeout expires before space becomes available.
        """
        with self.not_full:
            start = time.time()

            # Block until space exists.
            while len(self.queue) >= self.capacity:
                remaining = None
                if timeout is not None:
                    elapsed = time.time() - start
                    remaining = timeout - elapsed
                    if remaining <= 0:
                        return False  # Producer timed out

                self.not_full.wait(timeout=remaining)

            # Space available → enqueue item
            self.queue.append(item)
            self.not_empty.notify()  # Wake consumers
            return True

    # GET OPERATION (BLOCKING)
    def get(self, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Remove and return the next queue item. If queue is empty, block until
        a producer adds something or timeout occurs.

        Args:
            timeout: Optional max time to wait.

        Returns:
            The dequeued item, or None if timeout expires.
        """
        with self.not_empty:
            start = time.time()

            while len(self.queue) == 0:
                remaining = None
                if timeout is not None:
                    elapsed = time.time() - start
                    remaining = timeout - elapsed
                    if remaining <= 0:
                        return None  # Consumer timed out

                self.not_empty.wait(timeout=remaining)

            # Pop oldest item (FIFO)
            item = self.queue.popleft()
            self.not_full.notify()  # Wake producers
            return item

    # SIMPLE QUERY METHODS (non-blocking)
    def size(self) -> int:
        with self.lock:
            return len(self.queue)

    def is_empty(self) -> bool:
        with self.lock:
            return len(self.queue) == 0

    def is_full(self) -> bool:
        with self.lock:
            return len(self.queue) >= self.capacity


# Part 3: Container(Thread-Safe Storage)
class Container:
    """
    A minimal thread-safe structure used as:
        - producer input source
        - consumer output storage

    Provides simple FIFO ordering (pop from front) and strict locking.
    """

    def __init__(self, items: Optional[List[Any]] = None):
        self.items = list(items) if items else []
        self.lock = threading.Lock()

    def add(self, item: Any):
        """Append an item safely."""
        with self.lock:
            self.items.append(item)

    def remove(self) -> Optional[Any]:
        """Pop an item from the front safely."""
        with self.lock:
            return self.items.pop(0) if self.items else None

    def is_empty(self) -> bool:
        with self.lock:
            return len(self.items) == 0

    def size(self) -> int:
        with self.lock:
            return len(self.items)

    def get_all(self) -> List[Any]:
        """Return a shallow copy of current items."""
        with self.lock:
            return list(self.items)


# Part 4: Producer Thread
class Producer(threading.Thread):
    """
    Producer worker that:
        - Pulls items from the source container.
        - Attempts to push them into the bounded queue.
        - Honors production delays.
        - Stops once the source is exhausted or queue rejects items.

    This simulates an upstream system feeding data into a pipeline.
    """

    def __init__(
        self,
        source: Container,
        queue: BoundedBlockingQueue,
        producer_id: int = 1,
        production_delay: float = 0.1,
    ):
        super().__init__(name=f"Producer-{producer_id}")
        self.source = source
        self.queue = queue
        self.production_delay = production_delay
        self.items_produced = 0
        self._stop_event = threading.Event()

    def run(self):
        """Main loop: pull → delay → enqueue."""
        while not self._stop_event.is_set():

            # Source exhausted → producer exits
            item = self.source.remove()
            if item is None:
                break

            # Simulate real workload pacing
            if self.production_delay > 0:
                time.sleep(self.production_delay)

            # Attempt a timed enqueue to avoid deadlocks
            if self.queue.put(item, timeout=1.0):
                self.items_produced += 1
            else:
                # Queue stayed full → restore item and stop
                self.source.add(item)
                break

    def stop(self):
        """External stop signal."""
        self._stop_event.set()


# Part 5: Consumer Thread
class Consumer(threading.Thread):
    """
    Consumer worker that:
        - Pulls items from the queue.
        - Stores them into the destination container.
        - Honors consumption delays.
        - Automatically exits when queue stays empty long enough.

    Mimics downstream processes such as storage writers or processors.
    """

    def __init__(
        self,
        queue: BoundedBlockingQueue,
        destination: Container,
        consumer_id: int = 1,
        consumption_delay: float = 0.15,
    ):
        super().__init__(name=f"Consumer-{consumer_id}")
        self.queue = queue
        self.destination = destination
        self.consumption_delay = consumption_delay
        self.items_consumed = 0
        self._stop_event = threading.Event()

    def run(self):
        """Main loop: dequeue → delay → persist."""
        while not self._stop_event.is_set():

            item = self.queue.get(timeout=1.0)
            if item is None:
                break  # No more items forthcoming

            if self.consumption_delay > 0:
                time.sleep(self.consumption_delay)

            self.destination.add(item)
            self.items_consumed += 1

    def stop(self):
        """External stop signal."""
        self._stop_event.set()


# Part 6: ProducerConsumerSystem
class ProducerConsumerSystem:
    """
    High-level orchestrator that wires together:
        - source container
        - bounded queue
        - producer threads
        - consumer threads
        - destination container

    Once run(), the system:
        1. Starts all producers and consumers.
        2. Waits for producers to finish.
        3. Waits for consumers to drain the queue.
        4. Returns all consumed items.

    Represents a simplified ETL-style workflow.
    """

    def __init__(
        self,
        source_items: List[Any],
        queue_capacity: int = 5,
        num_producers: int = 1,
        num_consumers: int = 1,
        production_delay: float = 0.05,
        consumption_delay: float = 0.08,
    ):
        self.source = Container(source_items)
        self.destination = Container()
        self.queue = BoundedBlockingQueue(queue_capacity)

        # Create producer threads
        self.producers = [
            Producer(self.source, self.queue, i + 1, production_delay)
            for i in range(num_producers)
        ]

        # Create consumer threads
        self.consumers = [
            Consumer(self.queue, self.destination, i + 1, consumption_delay)
            for i in range(num_consumers)
        ]

    def run(self) -> List[Any]:
        """
        Execute the full pipeline to completion.

        Returns:
            A list of all items consumed by the system.
        """
        # Start all workers
        for p in self.producers:
            p.start()
        for c in self.consumers:
            c.start()

        # Wait for upstream to finish
        for p in self.producers:
            p.join()

        # Consumers finish once queue drains
        for c in self.consumers:
            c.join()

        return self.destination.get_all()

