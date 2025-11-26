"""
PyTest Suite for Assignment 1: Producer–Consumer Pattern.

Each test includes explicit comments describing the scenario and edge
cases being validated. Coverage includes:
- FIFO queue correctness
- Blocking semantics
- Thread safety
- Producer/consumer behavior
- End-to-end concurrency integration
"""

import time
import threading
from assignment1.producer_consumer import (
    Item,
    BoundedBlockingQueue,
    Container,
    Producer,
    Consumer,
    ProducerConsumerSystem,
)


# =============================================================================
# ITEM TESTS
# =============================================================================

def test_item_creation():
    """Test: Item initializes fields correctly and auto-generates timestamp."""
    item = Item(1, "hello")
    assert item.id == 1
    assert item.data == "hello"
    assert item.timestamp is not None


def test_item_repr_contains_data():
    """Test: __repr__ should contain id and data for debugging."""
    item = Item(10, "world")
    rep = repr(item)
    assert "10" in rep and "world" in rep


# =============================================================================
# QUEUE TESTS (FIFO + Blocking)
# =============================================================================

def test_queue_fifo_behavior():
    """Test: FIFO ordering — the queue must return items in insertion order."""
    q = BoundedBlockingQueue(capacity=5)
    q.put("a")
    q.put("b")
    q.put("c")

    assert q.get() == "a"
    assert q.get() == "b"
    assert q.get() == "c"
    assert q.is_empty()


def test_queue_blocks_put_when_full():
    """
    Edge Case: Queue is full → put() must block and eventually timeout.
    Validates producer-side blocking behavior.
    """
    q = BoundedBlockingQueue(capacity=1)
    q.put("x")  # queue full

    start = time.time()
    result = q.put("y", timeout=0.2)
    end = time.time()

    assert not result
    assert end - start >= 0.15


def test_queue_blocks_get_when_empty():
    """
    Edge Case: Queue empty → get() must block until timeout.
    Validates consumer-side blocking behavior.
    """
    q = BoundedBlockingQueue(capacity=2)

    start = time.time()
    item = q.get(timeout=0.2)
    end = time.time()

    assert item is None
    assert end - start >= 0.15


def test_queue_capacity_one_edge_case():
    """
    Edge Case: capacity=1 — smallest valid queue.
    Ensures correctness under minimal buffer size.
    """
    q = BoundedBlockingQueue(capacity=1)
    q.put("first")

    assert q.is_full()
    assert q.get() == "first"
    assert q.is_empty()


# =============================================================================
# CONTAINER TESTS
# =============================================================================

def test_container_basic_operations():
    """Test: FIFO behavior + None when empty."""
    c = Container()
    c.add("x")
    c.add("y")

    assert c.size() == 2
    assert c.remove() == "x"
    assert c.remove() == "y"
    assert c.remove() is None


def test_container_thread_safe_writes():
    """
    Concurrency Test: Multiple threads writing simultaneously.
    Ensures add() is race-free.
    """
    c = Container()

    def writer():
        for _ in range(100):
            c.add(1)

    threads = [threading.Thread(target=writer) for _ in range(3)]
    for t in threads: t.start()
    for t in threads: t.join()

    assert c.size() == 300


# =============================================================================
# PRODUCER TESTS
# =============================================================================

def test_producer_transfers_all_items():
    """
    Test: Producer should drain source container completely
    when queue is not a bottleneck.
    """
    src = Container([1, 2, 3])
    q = BoundedBlockingQueue(capacity=5)

    p = Producer(src, q, production_delay=0)
    p.start(); p.join()

    assert src.is_empty()
    assert q.size() == 3
    assert p.items_produced == 3


def test_producer_stops_when_queue_stays_full():
    """
    Edge Case: Producer encounters a full queue → must restore item and stop.
    Verifies timeout handling and upstream rollback behavior.
    """
    src = Container([10])
    q = BoundedBlockingQueue(capacity=1)
    q.put("pre-fill")

    p = Producer(src, q, production_delay=0)
    p.start(); p.join()

    assert src.size() == 1
    assert q.size() == 1
    assert p.items_produced == 0


# =============================================================================
# CONSUMER TESTS
# =============================================================================

def test_consumer_drains_queue():
    """Test: Consumer must consume all items until queue is empty."""
    q = BoundedBlockingQueue(capacity=5)
    dst = Container()

    for i in range(4):
        q.put(i)

    c = Consumer(q, dst, consumption_delay=0)
    c.start(); c.join()

    assert dst.size() == 4
    assert c.items_consumed == 4


def test_consumer_exits_when_queue_empty():
    """
    Edge Case: Queue starts empty → consumer should exit after timeout.
    Validates natural shutdown behavior.
    """
    q = BoundedBlockingQueue(capacity=3)
    dst = Container()

    c = Consumer(q, dst, consumption_delay=0)
    c.start(); c.join()

    assert dst.size() == 0
    assert c.items_consumed == 0


# =============================================================================
# BASIC CONCURRENCY TESTS
# =============================================================================

def test_basic_concurrent_put_get():
    """
    Concurrency Test: Parallel producer + consumer threads must transfer
    data reliably without corruption or loss.
    """
    q = BoundedBlockingQueue(capacity=5)
    results = []
    lock = threading.Lock()

    def producer():
        for i in range(10):
            q.put(i)

    def consumer():
        for _ in range(10):
            item = q.get(timeout=1)
            if item is not None:
                with lock:
                    results.append(item)

    t1 = threading.Thread(target=producer)
    t2 = threading.Thread(target=consumer)

    t1.start(); t2.start()
    t1.join(); t2.join()

    assert sorted(results) == list(range(10))


# =============================================================================
# SYSTEM TESTS (END-TO-END)
# =============================================================================

def test_system_single_producer_single_consumer():
    """System Test: Fully process 10 items end-to-end with 1P–1C."""
    items = [Item(i, f"data-{i}") for i in range(10)]
    system = ProducerConsumerSystem(
        items,
        queue_capacity=3,
        num_producers=1,
        num_consumers=1,
        production_delay=0,
        consumption_delay=0,
    )
    result = system.run()
    assert len(result) == 10


def test_system_multiple_producers_consumers():
    """System Test: Multi-producer + multi-consumer should process all items."""
    items = list(range(20))
    system = ProducerConsumerSystem(
        items,
        queue_capacity=5,
        num_producers=2,
        num_consumers=2,
        production_delay=0,
        consumption_delay=0,
    )
    result = system.run()
    assert len(result) == 20


def test_system_empty_source():
    """Edge Case: System should handle an empty input list."""
    system = ProducerConsumerSystem(
        source_items=[],
        queue_capacity=3,
        num_producers=1,
        num_consumers=1,
        production_delay=0,
        consumption_delay=0,
    )
    result = system.run()
    assert result == []


def test_system_small_queue_high_load():
    """
    Stress Test: Very small queue and high load should still eventually
    process everything without deadlocks.
    """
    items = list(range(30))
    system = ProducerConsumerSystem(
        items,
        queue_capacity=1,
        num_producers=2,
        num_consumers=2,
        production_delay=0,
        consumption_delay=0,
    )
    result = system.run()
    assert len(result) == 30