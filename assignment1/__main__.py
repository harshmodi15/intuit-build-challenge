"""
Assignment 1: Demo Runner

This file is executed when running:
    python -m assignment1

It uses the ProducerConsumerSystem from producer_consumer.py.
"""

from .producer_consumer import ProducerConsumerSystem, Item


def main():
    print("\n=== Producer–Consumer Demo (Assignment 1) ===\n")

    # Example dataset
    items = [Item(i, f"payload-{i}") for i in range(10)]

    system = ProducerConsumerSystem(
        source_items=items,
        queue_capacity=3,
        num_producers=1,
        num_consumers=1,
        production_delay=0.05,
        consumption_delay=0.08,
    )

    result = system.run()

    print(f"Demo complete. Items transferred: {len(result)}")
    print("Final destination contents:")
    for item in result:
        print("  ", item)


if __name__ == "__main__":
    main()