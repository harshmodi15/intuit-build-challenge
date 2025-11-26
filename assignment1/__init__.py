"""
Assignment 1: Producer–Consumer Pattern

This package exposes all components needed to demonstrate a classic
producer–consumer workflow implemented using thread synchronization
and a bounded blocking queue.

Public API:
    - Item: Basic data unit flowing through the system.
    - BoundedBlockingQueue: Thread-safe blocking FIFO queue.
    - Container: Thread-safe storage for producers/consumers.
    - Producer: Worker thread that feeds items into the queue.
    - Consumer: Worker thread that drains items from the queue.
    - ProducerConsumerSystem: Full end-to-end orchestrator.
"""

from .producer_consumer import (
    Item,
    BoundedBlockingQueue,
    Container,
    Producer,
    Consumer,
    ProducerConsumerSystem,
)

__all__ = [
    "Item",
    "BoundedBlockingQueue",
    "Container",
    "Producer",
    "Consumer",
    "ProducerConsumerSystem",
]